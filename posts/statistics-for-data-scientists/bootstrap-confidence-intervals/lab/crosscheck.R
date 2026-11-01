# Optional cross-check for "The Bootstrap: From Percentile to BCa, and Where It Breaks" (Statistics for Data
# Scientists, part 7). Bootstraps the law-school correlation with R's boot package, the reference implementation
# of Davison and Hinkley (1997), and writes everything bootstrap.py needs to recompute boot.ci's limits from R's
# own replicates:
#
#     Rscript crosscheck.R                 # writes crosscheck-r.csv beside this file
#
# Needs only base R and the boot package, which ships with R as a recommended package (run with R 4.5.2 and
# boot 1.3.32). Reads data/law_school_82.csv; writes crosscheck-r.csv; nothing else.

suppressPackageStartupMessages(library(boot))

law <- read.csv("data/law_school_82.csv", comment.char = "#")
s <- law[law$in_sample == 1, ]
s <- s[order(s$sample_order), c("lsat", "gpa")]

# The correlation and its nonparametric delta-method variance, sum(L^2) / n^2, where L holds the empirical
# influence values of the correlation. boot.ci's studentized interval reads the variance as the second statistic.
corr_var <- function(d, i) {
  x <- d[i, 1]
  y <- d[i, 2]
  n <- length(x)
  xs <- (x - mean(x)) / sqrt(mean((x - mean(x))^2))
  ys <- (y - mean(y)) / sqrt(mean((y - mean(y))^2))
  r <- mean(xs * ys)
  L <- xs * ys - r * (xs^2 + ys^2) / 2
  c(r, sum(L^2) / n^2)
}

set.seed(20261101)
b <- boot(s, corr_var, R = 2000)
ci <- boot.ci(b, conf = 0.95, type = c("norm", "basic", "stud", "perc", "bca"))
# The same studentized interval computed on Fisher's z scale, then mapped back.
ciz <- boot.ci(b, conf = 0.95, type = "stud", h = atanh, hdot = function(r) 1 / (1 - r^2), hinv = tanh)

# boot.ci's BCa needs empirical influence values for its acceleration. With R >= n and an index-type statistic,
# empinf() defaults to "reg": a regression of the replicates on how often each school was drawn.
L_reg <- empinf(b, index = 1, type = "reg")
L_jack <- empinf(b, index = 1, type = "jack")
acc <- function(L) sum(L^3) / (6 * sum(L^2)^1.5)
z0 <- qnorm(sum(b$t[, 1] < b$t0[1]) / b$R)
ci_jack <- boot.ci(b, conf = 0.95, type = "bca", L = L_jack)

lim <- function(m) m[1, ncol(m) - c(1, 0)]
rows <- rbind(
  data.frame(kind = "interval", key = "normal", v1 = ci$normal[1, 2], v2 = ci$normal[1, 3]),
  data.frame(kind = "interval", key = "basic", v1 = lim(ci$basic)[1], v2 = lim(ci$basic)[2]),
  data.frame(kind = "interval", key = "studentized", v1 = lim(ci$student)[1], v2 = lim(ci$student)[2]),
  data.frame(kind = "interval", key = "studentized_z", v1 = lim(ciz$student)[1], v2 = lim(ciz$student)[2]),
  data.frame(kind = "interval", key = "percentile", v1 = lim(ci$percent)[1], v2 = lim(ci$percent)[2]),
  data.frame(kind = "interval", key = "bca", v1 = lim(ci$bca)[1], v2 = lim(ci$bca)[2]),
  data.frame(kind = "interval", key = "bca_jack", v1 = lim(ci_jack$bca)[1], v2 = lim(ci_jack$bca)[2]),
  data.frame(kind = "constant", key = "t0", v1 = b$t0[1], v2 = b$t0[2]),
  data.frame(kind = "constant", key = "z0", v1 = z0, v2 = NA),
  data.frame(kind = "constant", key = "a_reg", v1 = acc(L_reg), v2 = NA),
  data.frame(kind = "constant", key = "a_jack", v1 = acc(L_jack), v2 = NA),
  data.frame(kind = "constant", key = "versions", v1 = paste(R.version$major, R.version$minor, sep = "."),
             v2 = as.character(packageVersion("boot"))),
  data.frame(kind = "influence", key = seq_along(L_reg), v1 = L_reg, v2 = L_jack),
  data.frame(kind = "replicate", key = seq_len(b$R), v1 = b$t[, 1], v2 = b$t[, 2])
)
write.csv(format(rows, digits = 17), "crosscheck-r.csv", row.names = FALSE, quote = FALSE)
cat(sprintf("R %s, boot %s, R = %d replicates: r = %.6f, z0 = %.4f, a (reg) = %.5f, a (jack) = %.5f\n",
            rows$v1[rows$key == "versions"], rows$v2[rows$key == "versions"], b$R, b$t0[1], z0, acc(L_reg), acc(L_jack)))
for (k in c("normal", "basic", "studentized", "studentized_z", "percentile", "bca", "bca_jack")) {
  r <- rows[rows$kind == "interval" & rows$key == k, ]
  cat(sprintf("  %-14s %.4f to %.4f\n", k, as.numeric(r$v1), as.numeric(r$v2)))
}
cat("wrote crosscheck-r.csv\n")
