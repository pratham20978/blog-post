# R cross-check for "Linear Regression by Hand: Every Number in the Summary" (Statistics for Data Scientists, part 13).
#
# Optional. Fits the lab's models with base R's lm (R's reference implementation of least squares) and writes every
# number it compares to crosscheck-R.csv, which regression.py reads when it is present. Base R only: no packages.
#
#   python regression.py nist --quick --out quick.json     # first: downloads NIST's files into .nist/
#   Rscript crosscheck.R                                   # then: writes crosscheck-R.csv beside this file
#
# Run it from this folder. Values are written with 17 significant digits, so a difference of 1e-15 is visible.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- sub("^--file=", "", args[grep("^--file=", args)])
here <- if (length(file_arg)) dirname(normalizePath(file_arg)) else getwd()
data_dir <- file.path(here, "data")
nist_dir <- file.path(here, ".nist")
out <- list()
put <- function(key, value) out[[key]] <<- value

read_lab_csv <- function(name) read.csv(file.path(data_dir, name), comment.char = "#")

# Part 8's tests as regressions: the sleep data with a drug dummy, then with patient dummies.
sl <- read_lab_csv("student1908_sleep.csv")
long <- data.frame(extra = c(sl$drug_1, sl$drug_2), drug = factor(rep(1:2, each = 10)),
                   patient = factor(rep(sl$patient, 2)))
f1 <- summary(lm(extra ~ drug, data = long))
f2 <- summary(lm(extra ~ drug + patient, data = long))
put("sleep_unpaired_t", coef(f1)["drug2", "t value"])
put("sleep_unpaired_p", coef(f1)["drug2", "Pr(>|t|)"])
put("sleep_paired_t", coef(f2)["drug2", "t value"])
put("sleep_paired_p", coef(f2)["drug2", "Pr(>|t|)"])

pg <- read_lab_csv("plant_growth.csv")
pg$group <- factor(pg$group, levels = c("ctrl", "trt1", "trt2"))
a <- anova(lm(weight ~ 1, data = pg), lm(weight ~ group, data = pg))
put("plants_F", a$F[2])
put("plants_p", a$`Pr(>F)`[2])

# NIST: Longley and Filip from the files regression.py downloaded and hash-checked.
read_nist <- function(name) {
  path <- file.path(nist_dir, paste0(name, ".dat"))
  if (!file.exists(path)) stop("run 'python regression.py nist' first: it downloads ", name, ".dat into .nist/")
  lines <- readLines(path)
  read.table(text = lines[61:length(lines)])
}
lo <- read_nist("Longley")
names(lo) <- c("Employed", "Deflator", "GNP", "Unemployed", "Armed", "Population", "Year")
fl <- lm(Employed ~ Deflator + GNP + Unemployed + Armed + Population + Year, data = lo)
sl_lo <- summary(fl)
for (j in seq_along(coef(fl))) {
  put(sprintf("Longley_default_b%d", j - 1), coef(fl)[j])
  put(sprintf("Longley_se%d", j - 1), coef(sl_lo)[j, "Std. Error"])
}
put("Longley_default_rank", fl$rank)
put("Longley_sigma", sl_lo$sigma)
put("Longley_r2", sl_lo$r.squared)
put("Longley_adj_r2", sl_lo$adj.r.squared)
put("Longley_F", unname(sl_lo$fstatistic["value"]))
put("Longley_F_p", pf(sl_lo$fstatistic["value"], sl_lo$fstatistic["numdf"], sl_lo$fstatistic["dendf"], lower.tail = FALSE))
put("Longley_logLik", as.numeric(logLik(fl)))
put("Longley_logLik_df", attr(logLik(fl), "df"))
put("Longley_AIC", AIC(fl))
put("Longley_BIC", BIC(fl))

fi <- read_nist("Filip")
names(fi) <- c("y", "x")
filip_formula <- y ~ x + I(x^2) + I(x^3) + I(x^4) + I(x^5) + I(x^6) + I(x^7) + I(x^8) + I(x^9) + I(x^10)
for (tag in c("default", "tol1e10")) {
  fit <- if (tag == "default") lm(filip_formula, data = fi) else lm(filip_formula, data = fi, tol = 1e-10)
  b <- coef(fit)
  for (j in seq_along(b)) put(sprintf("Filip_%s_b%d", tag, j - 1), b[j])    # NA where lm dropped the column
  put(sprintf("Filip_%s_rank", tag), fit$rank)
}

# ToothGrowth: supplement x doublings of dose from 1 mg, and the lack-of-fit test against the six cell means.
tg <- read_lab_csv("toothgrowth.csv")
tg$OJ <- as.numeric(tg$supp == "OJ")
tg$z <- log2(tg$dose)
ft <- lm(len ~ OJ * z, data = tg)
put("teeth_OJ", coef(ft)["OJ"])
put("teeth_OJ_se", coef(summary(ft))["OJ", "Std. Error"])
put("teeth_inter", coef(ft)["OJ:z"])
cells <- lm(len ~ interaction(supp, dose), data = tg)
put("teeth_lof_F", anova(ft, cells)$F[2])

vc <- subset(tg, supp == "VC")
fv <- lm(len ~ z, data = vc)
nd <- data.frame(z = log2(1.5))
ci <- predict(fv, nd, interval = "confidence")
pi <- predict(fv, nd, interval = "prediction")
put("vc_mean", ci[1, "fit"]); put("vc_ci_lo", ci[1, "lwr"]); put("vc_ci_hi", ci[1, "upr"])
put("vc_pi_lo", pi[1, "lwr"]); put("vc_pi_hi", pi[1, "upr"])

res <- data.frame(key = names(out), value = vapply(out, function(v) trimws(formatC(as.numeric(v), digits = 17, format = "g")),
                                                    character(1)))
writeLines(c(paste0("# Written by crosscheck.R with ", R.version.string, "; base R only."),
             "key,value", paste(res$key, res$value, sep = ",")), file.path(here, "crosscheck-R.csv"))
cat("wrote crosscheck-R.csv:", nrow(res), "values\n")
