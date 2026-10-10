"""Backbone census for "Diffusion Backbones, U-Net to DiT".

Builds three real denoiser architectures and measures what the article reports:

  unet       Stable Diffusion 1.5's U-Net, from its published config: every block's
             tensor shapes, the skip stack, parameters and FLOPs per resolution level.
  dit        DiT-XL at patch sizes 8, 4 and 2: tokens, parameters, FLOPs, and the
             share of FLOPs spent inside attention.
  mmdit      Stable Diffusion 3's MM-DiT at depth 24 (the 2B model): parameters per
             stream, and where one 1024x1024 call spends its FLOPs.
  attention  one attention layer timed and memory-profiled on this CPU, naive
             (materialised scores) against PyTorch's fused kernel, as tokens grow.
  memory     bytes for weights, optimizer state and one attention map, per model.
  patch      the worked example: patchify part 1's 4x4 patch at two patch sizes.

Every model is built on PyTorch's "meta" device, which tracks shapes without
allocating memory or computing values. Shapes, parameter counts and FLOP counts are
exact there; nothing is downloaded and no weights are needed. Only the attention
sweep executes real arithmetic.

FLOP convention: one multiply-add = 2 FLOPs (torch.utils.flop_counter). The DiT
paper reports the same quantity in multiply-adds, so its "Gflops" equal our GMAC.

Run:  python census.py              (all sections, writes captures.json)
      python census.py unet dit     (selected sections, prints only)
"""

import json
import math
import platform
import statistics
import sys
import time
from collections import defaultdict
from datetime import date

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.flop_counter import FlopCounterMode

import diffusers
from diffusers import SD3Transformer2DModel, UNet2DConditionModel

META = torch.device("meta")
OUT = {}

# ---------------------------------------------------------------------------
# Configs
# ---------------------------------------------------------------------------

# stable-diffusion-v1-5/stable-diffusion-v1-5, unet/config.json (copied verbatim,
# minus the private "_class_name"/"_diffusers_version" keys).
SD15_UNET = {
    "act_fn": "silu", "attention_head_dim": 8,
    "block_out_channels": [320, 640, 1280, 1280],
    "center_input_sample": False, "cross_attention_dim": 768,
    "down_block_types": ["CrossAttnDownBlock2D", "CrossAttnDownBlock2D",
                         "CrossAttnDownBlock2D", "DownBlock2D"],
    "downsample_padding": 1, "flip_sin_to_cos": True, "freq_shift": 0,
    "in_channels": 4, "layers_per_block": 2, "mid_block_scale_factor": 1,
    "norm_eps": 1e-05, "norm_num_groups": 32, "out_channels": 4, "sample_size": 64,
    "up_block_types": ["UpBlock2D", "CrossAttnUpBlock2D", "CrossAttnUpBlock2D",
                       "CrossAttnUpBlock2D"],
}

# DiT-XL from facebookresearch/DiT models.py: depth 28, width 1152, 16 heads,
# 1000 ImageNet classes, a learned variance output (so 2 x 4 output channels).
DIT_XL = dict(depth=28, hidden=1152, heads=16, in_ch=4, num_classes=1000)

# SD3's MM-DiT: the paper sets width 64*d, d heads, MLP 4*64*d. d = 24 is the 2B
# model and d = 38 the 8B model. The remaining arguments follow diffusers'
# scripts/convert_sd3_to_diffusers.py for SD3.0.
def sd3_kwargs(depth):
    return dict(sample_size=128, patch_size=2, in_channels=16, out_channels=16,
                num_layers=depth, attention_head_dim=64, num_attention_heads=depth,
                joint_attention_dim=4096, caption_projection_dim=64 * depth,
                pooled_projection_dim=2048, pos_embed_max_size=192)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def nparams(module):
    return sum(p.numel() for p in module.parameters())


def op_class(op):
    """Sort an aten op into the three kinds of work a denoiser does."""
    name = str(op)
    if "convolution" in name:
        return "conv"
    if "bmm" in name or "scaled_dot_product" in name:
        return "attention_core"  # QK^T and softmax(QK^T)V
    return "linear"  # mm / addmm: projections, MLPs, embeddings


def count_flops(fn):
    """Run fn under a FLOP counter; return {module path: {op class: flops}}."""
    counter = FlopCounterMode(display=False, depth=None)
    with counter, torch.no_grad():
        result = fn()
    table = {}
    for path, ops in counter.get_flop_counts().items():
        split = defaultdict(int)
        for op, n in ops.items():
            split[op_class(op)] += n
        table[path] = dict(split)
    return table, result


def total(split):
    return sum(split.values())


def shape(t):
    return list(t.shape)


def g(x):
    return round(x / 1e9, 2)


# ---------------------------------------------------------------------------
# Worked example: patchify part 1's 4x4 noisy patch
# ---------------------------------------------------------------------------

# Part 1's x_t at abar = 0.64 (series context file), one channel.
X_T = [[0.43, 1.32, 0.03, -1.34],
       [1.15, -0.45, -0.59, -0.30],
       [1.19, 0.26, -1.13, -0.67],
       [-0.43, 0.38, 0.19, -1.46]]


def patchify(grid, p):
    """Cut a square grid into p x p patches, read row-major, one token per patch."""
    n = len(grid)
    tokens = []
    for r in range(0, n, p):
        for c in range(0, n, p):
            tokens.append([grid[r + i][c + j] for i in range(p) for j in range(p)])
    return tokens


def section_patch():
    out = {}
    for p in (4, 2, 1):
        toks = patchify(X_T, p)
        out[f"p{p}"] = {"tokens": len(toks), "token_length": len(toks[0]),
                        "attention_pairs": len(toks) ** 2, "values": toks}
    # 2x2 average pool: the U-Net's way of reaching a coarser grid.
    pooled = [[round(sum(X_T[r + i][c + j] for i in (0, 1) for j in (0, 1)) / 4, 4)
               for c in (0, 2)] for r in (0, 2)]
    out["avgpool2"] = pooled
    # The same counts on a real latent: 512x512 image -> 4x64x64 latent.
    out["latent_64"] = {f"p{p}": (64 // p) ** 2 for p in (8, 4, 2, 1)}
    print("\n== patch: part 1's 4x4 x_t, patchified ==")
    for p in (4, 2, 1):
        d = out[f"p{p}"]
        print(f"  p={p}: {d['tokens']:>2} tokens of length {d['token_length']:>2}, "
              f"{d['attention_pairs']:>3} attention pairs")
    print("  p=2 tokens:", out["p2"]["values"])
    print("  2x2 average pool (U-Net view):", pooled)
    print("  64x64 latent tokens by patch size:", out["latent_64"])
    OUT["patch"] = out


# ---------------------------------------------------------------------------
# U-Net: Stable Diffusion 1.5
# ---------------------------------------------------------------------------

LEVEL_RES = {0: 64, 1: 32, 2: 16, 3: 8}


def unet_level(path):
    """Which resolution level a module path belongs to (mid block = level 3)."""
    parts = path.split(".")
    if "down_blocks" in parts:
        return int(parts[parts.index("down_blocks") + 1])
    if "up_blocks" in parts:
        return 3 - int(parts[parts.index("up_blocks") + 1])
    if "mid_block" in parts:
        return 3
    return None


def section_unet(execute=False):
    torch.manual_seed(0)
    with META:
        unet = UNet2DConditionModel(**SD15_UNET)
        x = torch.randn(1, 4, 64, 64)       # 512x512 image after the VAE (f = 8)
        t = torch.tensor([500])
        ctx = torch.randn(1, 77, 768)       # CLIP ViT-L/14 text tokens

    # Shape trace with forward hooks.
    trace = []

    def hook(name):
        def fn(mod, args, kwargs, out):
            inp = args[0] if args else kwargs.get("hidden_states")
            o = out[0] if isinstance(out, tuple) else out
            o = getattr(o, "sample", o)
            rec = {"module": name, "in": shape(inp), "out": shape(o),
                   "params": nparams(mod)}
            if name.startswith("up_blocks.") and name.count(".") == 1:
                skips = kwargs.get("res_hidden_states_tuple") or args[1]
                rec["skips_in"] = [shape(s) for s in skips]
            if name.startswith("down_blocks.") and name.count(".") == 1:
                rec["skips_out"] = [shape(s) for s in out[1]]
            trace.append(rec)
        return fn

    watch = ["conv_in", "conv_out", "mid_block"]
    for i in range(4):
        watch.append(f"down_blocks.{i}")
        watch.append(f"up_blocks.{i}")
    for name, mod in unet.named_modules():
        top = name.count(".") == 1 and name.split(".")[0] in ("down_blocks", "up_blocks")
        inner = any(k in name.split(".")[-2:-1] for k in ("resnets", "attentions"))
        sampler = name.endswith("downsamplers.0") or name.endswith("upsamplers.0")
        if name in watch or top or (inner and name.count(".") == 3) or sampler:
            mod.register_forward_hook(hook(name), with_kwargs=True)

    flops, y = count_flops(lambda: unet(x, t, encoder_hidden_states=ctx).sample)
    root = "UNet2DConditionModel"
    grand = flops["Global"]

    # Per-level parameters and FLOPs.
    lvl_p = defaultdict(int)
    for name, p in unet.named_parameters():
        lv = unet_level(name)
        lvl_p["other" if lv is None else lv] += p.numel()
    lvl_f = defaultdict(lambda: defaultdict(int))
    for path, split in flops.items():
        if not path.startswith(root + "."):
            continue
        rel = path[len(root) + 1:]
        depth = rel.count(".")
        # Count each FLOP once: at the block level (depth 1) or the top-level leaf.
        if rel.split(".")[0] in ("down_blocks", "up_blocks") and depth == 1:
            key = unet_level(rel)
        elif rel == "mid_block":
            key = 3
        elif depth == 0 and rel not in ("down_blocks", "up_blocks", "mid_block"):
            key = "other"
        else:
            continue
        for k, v in split.items():
            lvl_f[key][k] += v

    levels = []
    for lv in (0, 1, 2, 3, "other"):
        split = dict(lvl_f[lv])
        levels.append({
            "level": lv, "resolution": LEVEL_RES.get(lv),
            "tokens": LEVEL_RES[lv] ** 2 if lv in LEVEL_RES else None,
            "params": lvl_p[lv], "flops": total(split), "flops_split": split,
        })
    assert sum(l["params"] for l in levels) == nparams(unet)
    assert abs(sum(l["flops"] for l in levels) - total(grand)) < 1e3

    # conv_in's output is the first skip; each down block then pushes its own.
    skips = [next(r["out"] for r in trace if r["module"] == "conv_in")]
    skips += [s for r in trace if "skips_out" in r for s in r["skips_out"]]
    popped = [s for r in trace if "skips_in" in r for s in r["skips_in"]]
    assert sorted(map(tuple, skips)) == sorted(map(tuple, popped))
    skip_elems = sum(math.prod(s) for s in skips)
    res = {
        "config": "stable-diffusion-v1-5 unet/config.json",
        "input": shape(x), "context": shape(ctx), "output": shape(y),
        "params": nparams(unet),
        "params_groups": {n: nparams(m) for n, m in unet.named_children()},
        "flops": total(grand), "flops_split": grand,
        "levels": levels, "trace": trace,
        "skips": skips, "skip_elements": skip_elems,
        "skip_bytes_fp16": skip_elems * 2,
    }
    print("\n== unet: Stable Diffusion 1.5 U-Net, 512x512 image, batch 1 ==")
    print(f"  params {res['params']:,}   forward {g(res['flops'])} GFLOP "
          f"(conv {g(grand.get('conv', 0))}, linear {g(grand['linear'])}, "
          f"attention core {g(grand['attention_core'])})")
    print(f"  input {res['input']} + context {res['context']} -> output {res['output']}")
    for r in trace:
        extra = ""
        if "skips_out" in r:
            extra = "  pushes " + ", ".join("x".join(map(str, s[1:])) for s in r["skips_out"])
        if "skips_in" in r:
            extra = "  pops " + ", ".join("x".join(map(str, s[1:])) for s in r["skips_in"])
        if r["module"].count(".") <= 1:
            print(f"  {r['module']:<16} {str(r['in']):<20} -> {str(r['out']):<20}"
                  f" {r['params']/1e6:7.1f}M{extra}")
    print(f"  skip stack: {len(skips)} tensors, {skip_elems:,} values "
          f"= {skip_elems*2/1e6:.1f} MB in fp16 per image")
    for l in levels:
        s = l["flops_split"]
        print(f"  level {str(l['level']):<5} {str(l['resolution'] or '-'):>3}px "
              f"params {l['params']/1e6:6.1f}M ({100*l['params']/res['params']:4.1f}%)  "
              f"GFLOP {g(l['flops']):7.2f} ({100*l['flops']/res['flops']:4.1f}%)  "
              f"attn-core {g(s.get('attention_core', 0)):6.2f}")
    OUT["unet"] = res

    if execute:
        # Optional: allocate the real fp32 model (3.4 GB) and run it once on CPU.
        torch.manual_seed(0)
        real = UNet2DConditionModel(**SD15_UNET).eval()
        xr, cr = torch.randn(1, 4, 64, 64), torch.randn(1, 77, 768)
        t0 = time.perf_counter()
        with torch.no_grad():
            yr = real(xr, torch.tensor([500]), encoder_hidden_states=cr).sample
        OUT["unet"]["executed"] = {"output": shape(yr),
                                   "seconds": round(time.perf_counter() - t0, 2)}
        print(f"  executed on CPU: output {shape(yr)} in "
              f"{OUT['unet']['executed']['seconds']} s")


# ---------------------------------------------------------------------------
# DiT: a minimal implementation of facebookresearch/DiT's architecture
# ---------------------------------------------------------------------------

def sincos_2d(dim, grid):
    """Fixed 2-D sine-cosine position embedding (half the width per axis)."""
    def one_axis(d, pos):
        omega = 1.0 / 10000 ** (torch.arange(d // 2, dtype=torch.float64) / (d / 2))
        out = pos.reshape(-1, 1) * omega.reshape(1, -1)
        return torch.cat([out.sin(), out.cos()], dim=1)
    ys, xs = torch.meshgrid(torch.arange(grid, dtype=torch.float64),
                            torch.arange(grid, dtype=torch.float64), indexing="ij")
    return torch.cat([one_axis(dim // 2, ys), one_axis(dim // 2, xs)], dim=1).float()


def timestep_features(t, dim=256):
    half = dim // 2
    freqs = torch.exp(-math.log(10000) * torch.arange(half, device=t.device) / half)
    args = t[:, None].float() * freqs[None]
    return torch.cat([args.cos(), args.sin()], dim=-1)


def attention(q, k, v):
    """Plain scaled dot-product attention, written out so every matmul is visible."""
    scores = (q @ k.transpose(-2, -1)) * q.shape[-1] ** -0.5
    return scores.softmax(dim=-1) @ v


class DiTBlock(nn.Module):
    def __init__(self, d, heads):
        super().__init__()
        self.heads = heads
        self.norm1 = nn.LayerNorm(d, elementwise_affine=False, eps=1e-6)
        self.qkv = nn.Linear(d, 3 * d)
        self.proj = nn.Linear(d, d)
        self.norm2 = nn.LayerNorm(d, elementwise_affine=False, eps=1e-6)
        self.fc1, self.fc2 = nn.Linear(d, 4 * d), nn.Linear(4 * d, d)
        # adaLN-Zero: the condition regresses shift, scale and gate for both sublayers.
        self.ada = nn.Sequential(nn.SiLU(), nn.Linear(d, 6 * d))

    def forward(self, x, c):
        b, n, d = x.shape
        sh1, sc1, g1, sh2, sc2, g2 = self.ada(c).unsqueeze(1).chunk(6, dim=-1)
        h = self.norm1(x) * (1 + sc1) + sh1
        q, k, v = self.qkv(h).reshape(b, n, 3, self.heads, d // self.heads).permute(2, 0, 3, 1, 4)
        a = attention(q, k, v).transpose(1, 2).reshape(b, n, d)
        x = x + g1 * self.proj(a)
        h = self.norm2(x) * (1 + sc2) + sh2
        return x + g2 * self.fc2(F.gelu(self.fc1(h), approximate="tanh"))


class DiT(nn.Module):
    def __init__(self, input_size=32, patch=2, in_ch=4, hidden=1152, depth=28, heads=16,
                 num_classes=1000):
        super().__init__()
        self.p, self.out_ch = patch, 2 * in_ch          # noise + variance
        self.patch_embed = nn.Conv2d(in_ch, hidden, patch, stride=patch)
        grid = input_size // patch
        # Frozen, but a Parameter in the official code, so it is counted the same way.
        self.pos = nn.Parameter(sincos_2d(hidden, grid)[None], requires_grad=False)
        self.t_mlp = nn.Sequential(nn.Linear(256, hidden), nn.SiLU(), nn.Linear(hidden, hidden))
        self.y_embed = nn.Embedding(num_classes + 1, hidden)  # +1: the "no class" token for CFG
        self.blocks = nn.ModuleList(DiTBlock(hidden, heads) for _ in range(depth))
        self.final_norm = nn.LayerNorm(hidden, elementwise_affine=False, eps=1e-6)
        self.final_ada = nn.Sequential(nn.SiLU(), nn.Linear(hidden, 2 * hidden))
        self.final = nn.Linear(hidden, patch * patch * self.out_ch)

    def forward(self, x, t, y):
        b, c, hgt, wid = x.shape
        x = self.patch_embed(x).flatten(2).transpose(1, 2) + self.pos   # B, N, D
        cond = self.t_mlp(timestep_features(t)) + self.y_embed(y)
        for blk in self.blocks:
            x = blk(x, cond)
        shift, scale = self.final_ada(cond).unsqueeze(1).chunk(2, dim=-1)
        x = self.final(self.final_norm(x) * (1 + scale) + shift)        # B, N, p*p*2C
        gh, gw, p = hgt // self.p, wid // self.p, self.p
        x = x.reshape(b, gh, gw, p, p, self.out_ch).permute(0, 5, 1, 3, 2, 4)
        return x.reshape(b, self.out_ch, gh * p, gw * p)


# DiT paper, Table 4 (ImageNet, 400K steps, FID-50K without guidance) and Section 5.
DIT_PAPER = {(256, 8): (7.39, 676, 106.41), (256, 4): (29.05, 675, 43.01),
             (256, 2): (118.64, 675, 19.47), (512, 2): (524.60, 675, None)}


def section_dit():
    rows = []
    for image, p in ((256, 8), (256, 4), (256, 2), (512, 2)):
        lat = image // 8
        with META:
            m = DiT(input_size=lat, patch=p, **{k: v for k, v in DIT_XL.items()
                                               if k != "in_ch"}, in_ch=4)
            x = torch.randn(1, 4, lat, lat)
            t, y = torch.tensor([500]), torch.tensor([207])
        flops, out = count_flops(lambda: m(x, t, y))
        grand = flops["Global"]
        tokens = (lat // p) ** 2
        paper = DIT_PAPER[(image, p)]
        rows.append({
            "name": f"DiT-XL/{p}", "image": image, "latent": [4, lat, lat],
            "patch": p, "tokens": tokens, "token_width": 1152,
            "params": nparams(m), "flops": total(grand), "gmac": total(grand) / 2e9,
            # adaLN-Zero's per-block projection (width -> 6 x width), summed over blocks.
            "adaln_params": sum(nparams(b.ada) for b in m.blocks),
            "flops_split": grand,
            "attention_share": grand["attention_core"] / total(grand),
            "output": shape(out),
            "paper_gflops": paper[0], "paper_params_M": paper[1], "paper_fid50k_400k": paper[2],
        })
    print("\n== dit: DiT-XL at three patch sizes (batch 1) ==")
    for r in rows:
        print(f"  {r['name']:<9} {r['image']}px latent {r['latent']} -> {r['tokens']:>4} tokens"
              f"  params {r['params']/1e6:6.1f}M (paper {r['paper_params_M']}M)"
              f"  {r['gmac']:7.2f} GMAC (paper {r['paper_gflops']} 'Gflops')"
              f"  attention core {100*r['attention_share']:4.1f}%"
              f"  adaLN {100*r['adaln_params']/r['params']:4.1f}% of params")
    OUT["dit"] = rows


# ---------------------------------------------------------------------------
# MM-DiT: Stable Diffusion 3, depth 24
# ---------------------------------------------------------------------------

def stream_of(name):
    """Assign an SD3 parameter or module path to the image stream, text stream or shared."""
    text_keys = ("norm1_context", "norm2_context", "ff_context", "add_q_proj",
                 "add_k_proj", "add_v_proj", "to_add_out", "norm_added_q", "norm_added_k")
    if "transformer_blocks" not in name:
        return "outside_blocks"
    return "text" if any(k in name for k in text_keys) else "image"


def section_mmdit():
    res = {}
    for depth in (24, 38):
        with META:
            m = SD3Transformer2DModel(**sd3_kwargs(depth))
        split = defaultdict(int)
        for name, p in m.named_parameters():
            split[stream_of(name)] += p.numel()
        res[f"d{depth}"] = {"params": nparams(m), "params_split": dict(split),
                            "width": 64 * depth, "heads": depth}
    # One 1024x1024 call of the d=24 model: 16x128x128 latent, 77 CLIP + 77 T5 tokens.
    with META:
        m = SD3Transformer2DModel(**sd3_kwargs(24))
        x = torch.randn(1, 16, 128, 128)
        txt = torch.randn(1, 154, 4096)
        pooled = torch.randn(1, 2048)
        t = torch.tensor([500.0])
    flops, out = count_flops(lambda: m(hidden_states=x, encoder_hidden_states=txt,
                                       pooled_projections=pooled, timestep=t).sample)
    # The counter credits a FLOP to a module and to all its ancestors, so read each
    # FLOP once: projections and MLPs at their leaf modules, and the joint
    # QK^T / softmax-V matmuls at the attention module that runs them.
    by_stream = defaultdict(int)
    root = "SD3Transformer2DModel."
    for path, sp in flops.items():
        if not path.startswith(root):
            continue
        rel = path[len(root):]
        if rel.endswith(".attn"):
            by_stream["joint_attention_core"] += sp.get("attention_core", 0)
        elif not any(True for _ in m.get_submodule(rel).children()):
            by_stream[stream_of(rel)] += total(sp)
    grand = flops["Global"]
    joint_tokens = 4096 + 154
    res["call_1024"] = {
        "latent": shape(x), "image_tokens": 4096, "text_tokens": 154,
        "joint_tokens": joint_tokens, "output": shape(out),
        "flops": total(grand), "flops_split": grand,
        "flops_by_stream": dict(by_stream),
    }
    covered = sum(res["call_1024"]["flops_by_stream"].values())
    print("\n== mmdit: SD3 MM-DiT ==")
    for depth in (24, 38):
        r = res[f"d{depth}"]
        s = r["params_split"]
        print(f"  d={depth}: width {r['width']}, {r['heads']} heads, params {r['params']:,}"
              f"  (image stream {s['image']/1e6:.0f}M, text stream {s['text']/1e6:.0f}M,"
              f" outside blocks {s['outside_blocks']/1e6:.0f}M)")
    c = res["call_1024"]
    print(f"  d=24 at 1024px: latent {c['latent']} -> {c['image_tokens']} image + "
          f"{c['text_tokens']} text = {c['joint_tokens']} joint tokens, "
          f"{g(c['flops'])} GFLOP")
    for k, v in c["flops_by_stream"].items():
        print(f"    {k:<22} {g(v):8.1f} GFLOP ({100*v/c['flops']:4.1f}%)")
    print(f"    (blocks covered: {100*covered/c['flops']:.1f}% of the call)")
    OUT["mmdit"] = res


# ---------------------------------------------------------------------------
# Attention cost against token count
# ---------------------------------------------------------------------------

def block_flops(n, d=1152, heads=16):
    """FLOPs of one DiT block at n tokens, split into attention core and the rest."""
    with META:
        blk = DiTBlock(d, heads)
        x, c = torch.randn(1, n, d), torch.randn(1, d)
    flops, _ = count_flops(lambda: blk(x, c))
    s = flops["Global"]
    return s.get("attention_core", 0), s.get("linear", 0)


def time_it(fn, repeats):
    fn()  # warm-up
    runs = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        runs.append(time.perf_counter() - t0)
    return statistics.median(runs)


def alloc_profile(fn):
    """Largest single allocation and total bytes allocated while fn runs (CPU)."""
    from torch.profiler import ProfilerActivity, profile
    fn()
    with profile(activities=[ProfilerActivity.CPU], profile_memory=True) as prof:
        fn()
    ev = prof.key_averages()
    return (max(e.self_cpu_memory_usage for e in ev),
            sum(e.self_cpu_memory_usage for e in ev if e.self_cpu_memory_usage > 0))


def section_attention():
    d, heads = 1152, 16
    hd = d // heads
    flop_rows = []
    for n in (64, 256, 1024, 4096, 16384):
        core, lin = block_flops(n, d, heads)
        flop_rows.append({"tokens": n, "attention_core": core, "linear": lin,
                          "share": core / (core + lin),
                          "model_share": n / (n + 6 * d)})
    torch.manual_seed(0)
    time_rows = []
    for n in (256, 1024, 2048, 4096):
        q, k, v = (torch.randn(1, heads, n, hd) for _ in range(3))
        naive = lambda: attention(q, k, v)
        fused = lambda: F.scaled_dot_product_attention(q, k, v)
        reps = 7 if n <= 1024 else 3
        tn, tf = time_it(naive, reps), time_it(fused, reps)
        mn, totn = alloc_profile(naive)
        mf, totf = alloc_profile(fused)
        assert torch.allclose(naive(), fused(), atol=1e-4)
        time_rows.append({"tokens": n, "naive_ms": round(tn * 1e3, 2),
                          "fused_ms": round(tf * 1e3, 2),
                          "naive_largest_alloc_MB": round(mn / 1e6, 2),
                          "fused_largest_alloc_MB": round(mf / 1e6, 2),
                          "naive_total_alloc_MB": round(totn / 1e6, 2),
                          "fused_total_alloc_MB": round(totf / 1e6, 2),
                          "score_matrix_MB_fp32": heads * n * n * 4 / 1e6})
    OUT["attention"] = {"width": d, "heads": heads, "head_dim": hd,
                        "flops": flop_rows, "cpu": time_rows,
                        "threads": torch.get_num_threads()}
    print(f"\n== attention: one DiT-XL block (width {d}, {heads} heads) ==")
    for r in flop_rows:
        print(f"  N={r['tokens']:>5}: attention core {g(r['attention_core']):8.2f} GFLOP, "
              f"rest {g(r['linear']):8.2f} GFLOP, core share {100*r['share']:4.1f}% "
              f"(model N/(N+6D) {100*r['model_share']:4.1f}%)")
    print(f"  one attention layer on this CPU ({torch.get_num_threads()} threads, fp32, batch 1):")
    for r in time_rows:
        print(f"  N={r['tokens']:>5}: naive {r['naive_ms']:8.2f} ms, largest alloc "
              f"{r['naive_largest_alloc_MB']:8.2f} MB | fused {r['fused_ms']:8.2f} ms, "
              f"largest alloc {r['fused_largest_alloc_MB']:6.2f} MB")


# ---------------------------------------------------------------------------
# Memory arithmetic
# ---------------------------------------------------------------------------

def section_memory():
    """Memory arithmetic in decimal units (1 GB = 10^9 bytes), so it can be checked by hand."""
    unet_p = OUT.get("unet", {}).get("params")
    if unet_p is None:
        with META:
            unet_p = nparams(UNet2DConditionModel(**SD15_UNET))
    dit_p = next((r["params"] for r in OUT.get("dit", []) if r["name"] == "DiT-XL/2"), None)
    if dit_p is None:
        with META:
            dit_p = nparams(DiT(patch=2, hidden=1152, depth=28, heads=16))
    sd3 = OUT.get("mmdit")
    if sd3 is None:
        with META:
            sd3 = {f"d{d}": {"params": nparams(SD3Transformer2DModel(**sd3_kwargs(d)))}
                   for d in (24, 38)}
    # name, params, heads, tokens in the largest attention, transformer width, layers
    models = [("SD 1.5 U-Net, 512px", unet_p, 8, 4096, None, None),
              ("DiT-XL/2, 256px", dit_p, 16, 256, 1152, 28),
              ("DiT-XL/2, 512px", dit_p, 16, 1024, 1152, 28),
              ("SD3 MM-DiT d=24, 1024px", sd3["d24"]["params"], 24, 4096 + 154, 1536, 24),
              ("SD3 MM-DiT d=38, 1024px", sd3["d38"]["params"], 38, 4096 + 154, 2432, 38)]
    rows = []
    for name, p, h, n, width, layers in models:
        row = {
            "model": name, "params": p,
            "weights_fp32_GB": p * 4 / 1e9,
            "weights_bf16_GB": p * 2 / 1e9,
            # Mixed-precision Adam (ZeRO's accounting): 2 + 2 + 12 bytes per parameter.
            "train_state_GB": p * 16 / 1e9,
            "attention_tokens": n, "attention_heads": h,
            # One layer's softmax(QK^T) for one image, all heads, 2 bytes per score.
            "one_score_matrix_fp16_MB": h * n * n * 2 / 1e6,
        }
        if width:
            # Korthikanti et al. (2023), eq. 1: bytes of activations a layer keeps for the
            # backward pass, s tokens, batch 1, width h, a heads: s*h*(34 + 5*a*s/h).
            # The 5*a*s/h part is the s^2 attention scores; fused attention drops it.
            full = layers * n * width * (34 + 5 * h * n / width)
            linear_only = layers * n * width * 34
            row.update({"train_activations_GB": full / 1e9,
                        "train_activations_no_scores_GB": linear_only / 1e9})
        rows.append(row)
    OUT["memory"] = rows
    print("\n== memory: arithmetic, batch 1, decimal units ==")
    for r in rows:
        line = (f"  {r['model']:<25} {r['params']/1e9:5.3f}B params: weights "
                f"{r['weights_fp32_GB']:5.2f} GB fp32 / {r['weights_bf16_GB']:5.2f} GB bf16, "
                f"Adam state {r['train_state_GB']:6.1f} GB, one {r['attention_heads']}-head "
                f"score matrix at N={r['attention_tokens']}: {r['one_score_matrix_fp16_MB']:7.1f} MB")
        if "train_activations_GB" in r:
            line += (f", activations {r['train_activations_GB']:6.2f} GB "
                     f"({r['train_activations_no_scores_GB']:5.2f} GB without scores)")
        print(line)


# ---------------------------------------------------------------------------

SECTIONS = {"patch": section_patch, "unet": section_unet, "dit": section_dit,
            "mmdit": section_mmdit, "attention": section_attention, "memory": section_memory}


def provenance():
    cpu = platform.processor() or platform.machine()
    try:
        with open("/proc/cpuinfo") as f:
            cpu = next(l.split(":", 1)[1].strip() for l in f if l.startswith("model name"))
    except (OSError, StopIteration):
        pass
    return {"date": date.today().isoformat(), "os": platform.platform(), "cpu": cpu,
            "python": platform.python_version(), "torch": torch.__version__,
            "diffusers": diffusers.__version__, "threads": torch.get_num_threads()}


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    chosen = args or list(SECTIONS)
    OUT["provenance"] = provenance()
    print("provenance:", OUT["provenance"])
    for name in chosen:
        if name == "unet":
            section_unet(execute="--execute" in sys.argv)
        else:
            SECTIONS[name]()
    if not args:
        with open("captures.json", "w") as f:
            json.dump(OUT, f, indent=1, default=str)
        print("\nwrote captures.json")
