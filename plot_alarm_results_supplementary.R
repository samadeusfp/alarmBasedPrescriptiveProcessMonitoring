library(ggplot2)
library(plyr)
library(RColorBrewer)
library(reshape2)

setwd("/home/irene/Repos/AlarmBasedProcessPrediction/results_lgbm_ratios_nottrunc/")
files <- list.files()
data <- data.frame()
for (file in files) {
  tmp <- read.table(file, sep=";", header=T)
  tmp$cls <- "lgbm"
  data <- rbind(data, tmp)  
}
setwd("/home/irene/Repos/AlarmBasedProcessPrediction/results_rf_ratios_nottrunc/")
files <- list.files()
for (file in files) {
  tmp <- read.table(file, sep=";", header=T)
  tmp$cls <- "rf"
  data <- rbind(data, tmp)  
}


data$metric <- gsub("_mean", "", data$metric)
#data$cost_weights_str <- sprintf("%s\n%s\n%s", data$c_miss, data$c_action, data$c_postpone)
data$ratio <- paste(data$c_miss, data$c_action, sep=":")

base_size <- 36
line_size <- 1
point_size <- 4
width <- 1300
height <- 900

data <- subset(data, dataset != "bpic2018")
data <- subset(data, dataset != "uwv")
data$method <- as.character(data$method)
data$dataset <- as.character(data$dataset)
data$method[data$method=="fixed0"] <- "always alarm"
data$method[data$method=="fixed110"] <- "never alarm"
data$method[data$method=="fixed50"] <- "tau=0.5"
data$method[data$method=="opt_threshold"] <- "optimized"
data$dataset[data$dataset=="uwv_all"] <- "uwv"
data$dataset[data$dataset=="traffic_fines_1"] <- "traffic_fines"

head(data)

color_palette <- c("#0072B2", "#000000", "#E69F00", "#009E73", "#56B4E9","#D55E00", "#999999", "#F0E442", "#CC79A7")
png("/home/irene/Repos/AlarmBasedProcessPrediction/images/results_ratios_lgbm.png", width=width, height=height)
ggplot(subset(data, cls=="lgbm" & c_postpone==0 & metric=="cost_avg" & !grepl("fixed", method)), aes(x=c_miss, y=value, color=method, shape=method)) + 
  geom_point(size=point_size) + geom_line(size=line_size) + scale_x_continuous(breaks=c(1,5,10,20),
                                                                               labels=c("1:1", "5:1", "10:1", "20:1"))+
  theme_bw(base_size=base_size) + ylab("Average cost per case") + xlab("c_out : c_in") + facet_wrap( ~ dataset, ncol=2) +
  scale_color_manual(values=color_palette) + theme(legend.position="top")
dev.off()

png("/home/irene/Repos/AlarmBasedProcessPrediction/images/results_ratios_rf.png", width=width, height=height)
ggplot(subset(data, cls=="rf" & c_postpone==0 & metric=="cost_avg" & !grepl("fixed", method)), aes(x=c_miss, y=value, color=method, shape=method)) + 
  geom_point(size=point_size) + geom_line(size=line_size) + scale_x_continuous(breaks=c(1,5,10,20),
                                                                               labels=c("1:1", "5:1", "10:1", "20:1"))+
  theme_bw(base_size=base_size) + ylab("Average cost per case") + xlab("c_out : c_in") + facet_wrap( ~ dataset, ncol=2) +
  scale_color_manual(values=color_palette) + theme(legend.position="top")
dev.off()

color_palette <- c("#0072B2", "#000000", "#E69F00", "#009E73", "#56B4E9","#D55E00", "#999999", "#F0E442", "#CC79A7")
png("/home/irene/Repos/AlarmBasedProcessPrediction/images/results_thresholds_lgbm.png", width=width, height=height)
ggplot(subset(data, cls=="lgbm" & c_postpone==0 & metric=="cost_avg"), aes(x=threshold, y=value, color=factor(ratio))) + 
  geom_point(size=point_size) + geom_line(size=line_size) + geom_point(data=subset(data, cls=="lgbm" & c_postpone==0 & metric=="cost_avg" & method=="optimized"), 
                                                                       size=4, color="red", stroke=2, shape=4, aes(x=threshold, y=value, color=factor(c_miss))) +
  theme_bw(base_size=base_size) + ylab("Average cost per case") + xlab("Threshold (tau)") + 
  facet_wrap( ~ dataset, scales="free", ncol=2) + scale_color_manual(values=color_palette, name="c_out:c_in")
dev.off()

png("/home/irene/Repos/AlarmBasedProcessPrediction/images/results_thresholds_rf.png", width=width, height=height)
ggplot(subset(data, cls=="rf" & c_postpone==0 & metric=="cost_avg"), aes(x=threshold, y=value, color=factor(ratio))) + 
  geom_point(size=point_size) + geom_line(size=line_size) + geom_point(data=subset(data, cls=="rf" & c_postpone==0 & metric=="cost_avg" & method=="optimized"), 
                                                                       size=4, color="red", stroke=2, shape=4, aes(x=threshold, y=value, color=factor(c_miss))) +
  theme_bw(base_size=base_size) + ylab("Average cost per case") + xlab("Threshold (tau)") + 
  facet_wrap( ~ dataset, scales="free", ncol=2) + scale_color_manual(values=color_palette, name="c_out:c_in")
dev.off()


dt_melt <- subset(data, method=="optimized" & metric %in% c("earliness", "fscore"))

png("/home/irene/Repos/AlarmBasedProcessPrediction/images/results_earliness_fscore_rf.png", width=width, height=height)
ggplot(subset(dt_melt, cls=="rf"), aes(x=c_miss, y=value, color=metric)) + 
  geom_point(size=point_size) + geom_line(size=line_size) +
  theme_bw(base_size=base_size) + ylab("value") + xlab("Ratio c_out:c_in") + facet_wrap( ~ dataset, scales="free", ncol=2)
dev.off()

png("/home/irene/Repos/AlarmBasedProcessPrediction/images/results_earliness_fscore_lgbm.png", width=width, height=height)
ggplot(subset(dt_melt, cls=="lgbm"), aes(x=c_miss, y=value, color=metric)) + 
  geom_point(size=point_size) + geom_line(size=line_size) +
  theme_bw(base_size=base_size) + ylab("value") + xlab("Ratio c_out:c_in") + facet_wrap( ~ dataset, scales="free", ncol=2)
dev.off()


### heatmaps effectiveness

setwd("/home/irene/Repos/AlarmBasedProcessPrediction/results_lgbm_ratios_nottrunc_effectiveness/")
files <- list.files()
data <- data.frame()
for (file in files) {
  tmp <- read.table(file, sep=";", header=T)
  tmp$cls <- "lgbm"
  data <- rbind(data, tmp)  
}
setwd("/home/irene/Repos/AlarmBasedProcessPrediction/results_rf_ratios_nottrunc_effectiveness/")
files <- list.files()
for (file in files) {
  tmp <- read.table(file, sep=";", header=T)
  tmp$cls <- "rf"
  data <- rbind(data, tmp)
}

data$metric <- gsub("_mean", "", data$metric)
data$ratio <- paste(data$c_miss, data$c_action, sep=":")
data$dataset <- as.character(data$dataset)
data$dataset[data$dataset=="uwv_all"] <- "uwv"
data$dataset[data$dataset=="traffic_fines_1"] <- "traffic_fines"
data$early_type <- as.character(data$early_type)
#data$early_type[data$early_type=="linear"] <- "linear eff. decay"
#data$early_type[data$early_type=="const"] <- "constant eff."

head(data)

dt_as_is <- subset(data, metric=="cost_avg_baseline")
dt_to_be <- subset(data, metric=="cost_avg")
dt_merged <- merge(dt_as_is[,-10], dt_to_be, by=c("dataset", "method", "c_miss", "c_action", "c_postpone", "eff", "early_type", "cls", "ratio"), suffixes=c("_as_is", "_to_be"))

dt_merged$benefit <- dt_merged$value_as_is - dt_merged$value_to_be
dt_merged$ratio <- as.factor(dt_merged$ratio)
dt_merged$ratio <- factor(dt_merged$ratio, levels(dt_merged$ratio)[c(2,4,5,7,1,3,6)])

base_size <- 30

png("/home/irene/Repos/AlarmBasedProcessPrediction/images/results_effectiveness_const_lgbm.png", width=width, height=height)
ggplot(subset(dt_merged, cls=="lgbm" & c_miss %in% c(1,2,3,5,10,20) & grepl("const", early_type)), aes(eff, factor(ratio))) + 
  geom_tile(aes(fill = benefit), colour = "white") + scale_x_continuous(breaks=c(0,0.2,0.4,0.6,0.8,1))+
  theme_bw(base_size=base_size) + scale_fill_gradient(low = "white", high = "black") + facet_wrap( ~ dataset, ncol=2) + 
  xlab("mitigation effectiveness (eff)") + ylab("c_out : c_in")
dev.off()

png("/home/irene/Repos/AlarmBasedProcessPrediction/images/results_effectiveness_const_rf.png", width=width, height=height)
ggplot(subset(dt_merged, cls=="rf" & c_miss %in% c(1,2,3,5,10,20) & grepl("const", early_type)), aes(eff, factor(ratio))) + 
  geom_tile(aes(fill = benefit), colour = "white") + scale_x_continuous(breaks=c(0,0.2,0.4,0.6,0.8,1))+
  theme_bw(base_size=base_size) + scale_fill_gradient(low = "white", high = "black") + facet_wrap( ~ dataset, ncol=2) + 
  xlab("mitigation effectiveness (eff)") + ylab("c_out : c_in")
dev.off()

png("/home/irene/Repos/AlarmBasedProcessPrediction/images/results_effectiveness_linear_lgbm.png", width=width, height=height)
ggplot(subset(dt_merged, cls=="lgbm" & c_miss %in% c(1,2,3,5,10,20) & !grepl("const", early_type)), aes(eff, factor(ratio))) + 
  geom_tile(aes(fill = benefit), colour = "white") + scale_x_continuous(breaks=c(0,0.2,0.4,0.6,0.8,1))+
  theme_bw(base_size=base_size) + scale_fill_gradient(low = "white", high = "black") + facet_wrap( ~ dataset, ncol=2) + 
  xlab("mitigation effectiveness (eff)") + ylab("c_out : c_in")
dev.off()

png("/home/irene/Repos/AlarmBasedProcessPrediction/images/results_effectiveness_linear_rf.png", width=width, height=height)
ggplot(subset(dt_merged, cls=="rf" & c_miss %in% c(1,2,3,5,10,20) & !grepl("const", early_type)), aes(eff, factor(ratio))) + 
  geom_tile(aes(fill = benefit), colour = "white") + scale_x_continuous(breaks=c(0,0.2,0.4,0.6,0.8,1))+
  theme_bw(base_size=base_size) + scale_fill_gradient(low = "white", high = "black") + facet_wrap( ~ dataset, ncol=2) + 
  xlab("mitigation effectiveness (eff)") + ylab("c_out : c_in")
dev.off()


### heatmaps cost of compensation

setwd("/home/irene/Repos/AlarmBasedProcessPrediction/results_lgbm_ratios_nottrunc_compensation/")
files <- list.files()
data <- data.frame()
for (file in files) {
  tmp <- read.table(file, sep=";", header=T)
  tmp$cls <- "lgbm"
  data <- rbind(data, tmp)  
}
setwd("/home/irene/Repos/AlarmBasedProcessPrediction/results_rf_ratios_nottrunc_compensation/")
files <- list.files()
for (file in files) {
  tmp <- read.table(file, sep=";", header=T)
  tmp$cls <- "rf"
  data <- rbind(data, tmp)  
}

data$metric <- gsub("_mean", "", data$metric)
data$ratio <- paste(data$c_miss, data$c_action, sep=":")
data$ratio_com <- ifelse(data$c_com==0, "1:0", ifelse(data$c_com > 1, sprintf("1:%s", data$c_com), sprintf("%s:1", 1/data$c_com)))
data$dataset <- as.character(data$dataset)
data$dataset[data$dataset=="uwv_all"] <- "uwv"
data$dataset[data$dataset=="traffic_fines_1"] <- "traffic_fines"
data$early_type <- as.character(data$early_type)
data$early_type[data$early_type=="linear"] <- "linearly increasing c_in"
data$early_type[data$early_type=="const"] <- "constant c_in"


head(data)

dt_as_is <- subset(data, metric=="cost_avg_baseline")
dt_to_be <- subset(data, metric=="cost_avg")
dt_merged <- merge(dt_as_is[,-10], dt_to_be, by=c("dataset", "method", "c_miss", "c_action", "c_postpone", "c_com", "early_type", "cls", "ratio", "ratio_com"), suffixes=c("_as_is", "_to_be"))

dt_merged$benefit <- dt_merged$value_as_is - dt_merged$value_to_be
dt_merged$ratio <- as.factor(dt_merged$ratio)
dt_merged$ratio <- factor(dt_merged$ratio, levels(dt_merged$ratio)[c(2,4,5,7,1,3,6)])
dt_merged$ratio_com <- as.factor(dt_merged$ratio_com)
dt_merged$ratio_com <- factor(dt_merged$ratio_com, levels(dt_merged$ratio_com)[c(1,13,10,2,14,12,11,3,5,7,9,4,6,8)])

png("/home/irene/Repos/AlarmBasedProcessPrediction/images/results_compensation_const_lgbm.png", width=width, height=height)
ggplot(subset(dt_merged, cls=="lgbm" & c_miss %in% c(1,2,3,5,10,20) & grepl("const", early_type) & ratio!="3:1" & 
                !(ratio_com%in%c("3:1", "1:3", "1:40", "40:1", NA, "20:1", "1:20"))), aes(ratio_com, factor(ratio))) + geom_tile(aes(fill = benefit), colour = "white") + 
  theme_bw(base_size=base_size) + scale_fill_gradient(low = "white", high = "black") + facet_wrap( ~ dataset, ncol=2) + 
  xlab("c_in : c_com") + ylab("c_out : c_in") +  theme(axis.text.x = element_text(size=20)) 
dev.off()

png("/home/irene/Repos/AlarmBasedProcessPrediction/images/results_compensation_const_rf.png", width=width, height=height)
ggplot(subset(dt_merged, cls=="rf" & c_miss %in% c(1,2,3,5,10,20) & grepl("const", early_type) & ratio!="3:1" & 
                !(ratio_com%in%c("3:1", "1:3", "1:40", "40:1", NA, "20:1", "1:20"))), aes(ratio_com, factor(ratio))) + geom_tile(aes(fill = benefit), colour = "white") + 
  theme_bw(base_size=base_size) + scale_fill_gradient(low = "white", high = "black") + facet_wrap( ~ dataset, ncol=2) + 
  xlab("c_in : c_com") + ylab("c_out : c_in") +  theme(axis.text.x = element_text(size=20)) 
dev.off()

png("/home/irene/Repos/AlarmBasedProcessPrediction/images/results_compensation_linear_lgbm.png", width=width, height=height)
ggplot(subset(dt_merged, cls=="lgbm" & c_miss %in% c(1,2,3,5,10,20) & !grepl("const", early_type) & ratio!="3:1" & 
                !(ratio_com%in%c("3:1", "1:3", "1:40", "40:1", NA, "20:1", "1:20"))), aes(ratio_com, factor(ratio))) + geom_tile(aes(fill = benefit), colour = "white") + 
  theme_bw(base_size=base_size) + scale_fill_gradient(low = "white", high = "black") + facet_wrap( ~ dataset, ncol=2) + 
  xlab("c_in : c_com") + ylab("c_out : c_in") +  theme(axis.text.x = element_text(size=20)) 
dev.off()

png("/home/irene/Repos/AlarmBasedProcessPrediction/images/results_compensation_linear_rf.png", width=width, height=height)
ggplot(subset(dt_merged, cls=="lgbm" & c_miss %in% c(1,2,3,5,10,20) & !grepl("const", early_type) & ratio!="3:1" & 
                !(ratio_com%in%c("3:1", "1:3", "1:40", "40:1", NA, "20:1", "1:20"))), aes(ratio_com, factor(ratio))) + geom_tile(aes(fill = benefit), colour = "white") + 
  theme_bw(base_size=base_size) + scale_fill_gradient(low = "white", high = "black") + facet_wrap( ~ dataset, ncol=2) + 
  xlab("c_in : c_com") + ylab("c_out : c_in") +  theme(axis.text.x = element_text(size=20)) 
dev.off()

# Reliability plot
setwd("/home/irene/Repos/AlarmBasedProcessPrediction/")

data <- read.table("predictions_calibrated/preds_bpic2017_refused.csv", sep=";", header=T)
data$params <- "calibrated"
tmp <- read.table("predictions/preds_bpic2017_refused.csv", sep=";", header=T)
tmp$params <- "original"
names(tmp)[names(tmp)=="preds"] <- "predicted_proba"
data <- rbind(data, tmp)
head(data)
head(tmp)

data$bin <- cut(data$predicted_proba, seq(0, 1, 0.05), seq(0, 0.95, 0.05))
# reliability plots
dt_reliability <- ddply(data, .(params, bin, prefix_nr), summarise, mean_predicted=mean(predicted_proba), ratio_pos=sum(actual)/length(actual))
head(dt_reliability)

png("/home/irene/Repos/AlarmBasedProcessPrediction/images/reliability_bpic2017_refused.png", width=width, height=height)
ggplot(dt_reliability, aes(x=mean_predicted, y=ratio_pos, color=params)) + geom_point() + geom_line() + 
  theme_bw(base_size=22) + facet_wrap(~prefix_nr) + geom_abline(slope=1, intercept=0) + scale_x_continuous(breaks=c(0,0.3,0.6,0.9))
dev.off()
