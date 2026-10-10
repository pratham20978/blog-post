# Asset manifest — diffusion-model-architecture

**Status: local draft assets ready for upload.** Upload the PNGs to the public
`media` bucket under the versioned object keys below, write the resulting URLs
to `urls.txt` in table order, then run Blog Forge's `fill_urls.py` command.

Every figure was redrawn on 2026-09-21 to depict its subject rather than label
it. `FIG_04` is laid out by Mermaid (`assets/fig-04-complete-system.mmd`,
rendered by `assets/_mermaid.py`) because the end-to-end graph is larger than a
hand-placed SVG can position — see blog-visuals section 5. Nothing here has been
published yet, so the object keys stay at `v1`.

| Placeholder | Local file | Suggested object key | Alt text |
|---|---|---|---|
| COVER | assets/cover.png | blog/diffusion-model-architecture/cover-v1.png | Tile fields of pure noise resolve left to right into a structured motif as the signal coefficient rises, past one highlighted denoising step |
| FIG_01 | assets/fig-01-forward-reverse.png | blog/diffusion-model-architecture/fig-01-forward-reverse-v1.png | One chain of noisy states with fixed forward noising above it, learned reverse denoising below it, and a closed-form shortcut from clean data to any level |
| FIG_02 | assets/fig-02-numeric-corruption.png | blog/diffusion-model-architecture/fig-02-numeric-corruption-v1.png | Three two-by-two matrices of numbers above the same three tensors as intensity, so 0.80 plus 0.12 equals 0.92 is visible rather than stated |
| FIG_03 | assets/fig-03-five-layer-system.png | blog/diffusion-model-architecture/fig-03-five-layer-system-v1.png | Five stacked design axes, each with a pictogram of itself, labelled with whether it survives a checkpoint swap or needs retraining |
| FIG_04 | assets/fig-04-complete-system.png | blog/diffusion-model-architecture/fig-04-complete-system-v1.png | An end-to-end graph placing the training loop, the conditioning chain and the N-step inference loop around the one shared learned denoiser |
| FIG_05 | assets/fig-05-unet-shapes.png | blog/diffusion-model-architecture/fig-05-unet-shapes-v1.png | A U-shaped trace whose block heights are spatial resolution and widths are channel count, with one dashed skip joining each resolution to its mirror |
| FIG_06 | assets/fig-06-time-residual-block.png | blog/diffusion-model-architecture/fig-06-time-residual-block-v1.png | A normalized feature map, a per-channel scale and shift bar for each of its six channels, and the modulated map those values produce |
| FIG_07 | assets/fig-07-self-vs-cross-attention.png | blog/diffusion-model-architecture/fig-07-self-vs-cross-attention-v1.png | Two score matrices drawn to scale: self-attention is a square N by N grid, cross-attention a narrow N by L grid over the prompt tokens |
| FIG_08 | assets/fig-08-dit-token-flow.png | blog/diffusion-model-architecture/fig-08-dit-token-flow-v1.png | The same latent under a two-by-two and a one-by-one patch lattice, flattened into token strips of visibly different length |
| FIG_09 | assets/fig-09-latent-diffusion.png | blog/diffusion-model-architecture/fig-09-latent-diffusion-v1.png | A pixel grid beside a latent drawn eight times smaller per side, with the denoiser loop attached to the small tensor and one decode back out |
| FIG_10 | assets/fig-10-prediction-geometry.png | blog/diffusion-model-architecture/fig-10-prediction-geometry-v1.png | In the clean-data and noise plane, x-t sits at coefficients 0.8 and 0.6, velocity sits perpendicular to it, and score points along negative noise |
| FIG_11 | assets/fig-11-noise-schedule.png | blog/diffusion-model-architecture/fig-11-noise-schedule-v1.png | Two panels plot the signal coefficient and the log signal-to-noise ratio against normalised timestep for the linear and cosine schedules |
| FIG_12 | assets/fig-12-training-loop.png | blog/diffusion-model-architecture/fig-12-training-loop-v1.png | A batch of six thumbnails at six different noise levels enters one shared network, producing one weighted loss and one parameter update |
| FIG_13 | assets/fig-13-sde-ode.png | blog/diffusion-model-architecture/fig-13-sde-ode-v1.png | Two lanes of trajectories between the same endpoints: jittering crossing paths for the reverse SDE, smooth non-crossing paths for the ODE |
| FIG_14 | assets/fig-14-sampler-decision.png | blog/diffusion-model-architecture/fig-14-sampler-decision-v1.png | A decision tree on whether the checkpoint may change, with each leaf carrying a sketch of the trajectory it produces, from many noisy steps to one jump |
| FIG_15 | assets/fig-15-cfg-step.png | blog/diffusion-model-architecture/fig-15-cfg-step-v1.png | Unconditional and conditional predictions define one ray, with guided tips marked at guidance scales of one, three and six along it |
| FIG_16 | assets/fig-16-backbone-map.png | blog/diffusion-model-architecture/fig-16-backbone-map-v1.png | A qualitative map placing U-Net, U-ViT, DiT and MM-DiT by how far their token mixing reaches and how separately they treat modalities |

Apply URLs after upload:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/diffusion-model-architecture/ urls.txt
```

Do not overwrite a published object. Increment the version suffix when an asset
changes so long-lived caches cannot serve an older image under the same URL.
