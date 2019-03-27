library(ggplot2)
library(plyr)
library(RColorBrewer)
library(reshape2)

setwd("/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/testresults/NonMyopicData")
files <- list.files()
data <- data.frame()
for (file in files) {
  tmp <- read.table(file, sep=";", header=T)
  tmp$cls <- "rf"
  data <- rbind(data, tmp)
}

data$metric <- gsub("_mean", "", data$metric)
data$ratio <- paste(data$c_miss, data$c_action, sep=":")

base_size <- 36
line_size <- 1
point_size <- 4

data <- subset(data, dataset != "bpic2018")
data <- subset(data, dataset != "uwv")
data$method <- as.character(data$method)
data$dataset <- as.character(data$dataset)
#data$method[data$method=="single_threshold"] <- "Single Alarm"
data$dataset[data$dataset=="uwv_all"] <- "uwv"
data$dataset[data$dataset=="traffic_fines_1"] <- "traffic_fines"

data$ratio <- as.factor(data$ratio)
data$ratio_com <- as.factor(data$c_com)


data <- subset(data, cls=="rf")
print(subset(data,method=="perfect_prediction"))

head(data)

dt_min_prefix <- subset(data, metric=="cost_avg" & method=="min_prefix")
dt_prefix <- subset(data, metric=="cost_avg" & method=="prefix_threshold")
dt_single <- subset(data, metric=="cost_avg" & method=="single_threshold")
dt_single$fscore <- subset(data, metric=="fscore" & method=="single_threshold")$value
dt_fire_delay <- subset(data, metric=="cost_avg" & method=="fire_delay")
dt_fire_delay$fscore <- subset(data, metric=="fscore" & method=="fire_delay")$value
dt_fire_delay_prefix <- subset(data, metric=="cost_avg" & method=="fire_delay_prefix_length")
dt_multi_fire_delay_prefix <- subset(data, metric=="cost_avg" & method=="1_vs_1_hierachical_fire_delay")



dt_merged <- merge(dt_min_prefix, dt_single, by=c("dataset", "c_miss", "c_action", "c_postpone", "c_com", "early_type", "cls", "ratio"), suffixes=c("_min_prefix", "_single"))
dt_merged$benefit_min_prefix <- dt_merged$value_min_prefix/dt_merged$value_single

dt_merged_fire_delay <- merge(dt_fire_delay, dt_single, by=c("dataset", "c_miss", "c_action", "c_postpone", "c_com", "early_type", "cls", "ratio"), suffixes=c("_fire_delay", "_single"))
dt_merged_fire_delay$benefit_fire_delay <- dt_merged_fire_delay$value_fire_delay/dt_merged_fire_delay$value_single
dt_merged_fire_delay$benefit_fscore <- dt_merged_fire_delay$fscore_fire_delay - dt_merged_fire_delay$fscore_single

dt_merged_fire_delay_prefix <- merge(dt_fire_delay_prefix, dt_single, by=c("dataset", "c_miss", "c_action", "c_postpone", "c_com", "early_type", "cls", "ratio"), suffixes=c("_fire_delay", "_single"))
dt_merged_fire_delay_prefix$benefit_fire_delay <- dt_merged_fire_delay_prefix$value_fire_delay/dt_merged_fire_delay_prefix$value_single


dt_merged_multi_fire_delay_prefix <- merge(dt_multi_fire_delay_prefix, dt_single, by=c("dataset", "c_miss", "c_action", "c_postpone", "c_com", "early_type", "cls", "ratio"), suffixes=c("_fire_delay", "_single"))
dt_merged_multi_fire_delay_prefix$benefit_fire_delay <- dt_merged_multi_fire_delay_prefix$value_fire_delay/dt_merged_multi_fire_delay_prefix$value_single


dt_merged2 <- merge(dt_prefix, dt_single, by=c("dataset", "c_miss", "c_action", "c_postpone", "c_com", "early_type", "cls", "ratio"), suffixes=c("_prefix", "_single"))
dt_merged2$benefit_prefix <-dt_merged2$value_prefix/dt_merged2$value_single
dt_merged2$benefit_fixed <- ifelse(dt_merged2$value_single > dt_merged2$value_prefix,1.0,0.0)
#print(min(dt_merged2$benefit_prefix))
#dt_merged2$benefit_fixed <- ifelse(dt_merged2$value_single < dt_merged2$value_prefix,-1.0,dt_merged2$benefit_fixed)

ggplot(dt_merged2, aes(x=benefit_prefix)) + 
  geom_histogram(color="black", fill="white",binwidth = 0.01) + facet_wrap(dataset ~ early_type, ncol=3) + xlab("Ratio baseline divided by two thresholds system") +
  theme(text = element_text(size=25))
ggsave("/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/testresults/NonMyopic/result_histogram_single_vs_prefix.pdf", width = 18, height = 16)

ggplot(dt_merged, aes(x=benefit_min_prefix)) + 
  geom_histogram(color="black", fill="white",binwidth = 0.01) + facet_wrap(dataset ~ early_type, ncol=3)
ggsave("/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/testresults/NonMyopic/result_histogram_single_vs_minprefix.pdf", width = 18, height = 16)

vec_traffic_linear <- subset(dt_merged2, dataset=="traffic_fines" & early_type=="linear" & benefit_prefix)
print("traffic_fines_single:")
print(max(vec_traffic_linear$benefit_prefix))
print(min(vec_traffic_linear$benefit_prefix))

vec_traffic_linear <- subset(dt_merged2, dataset=="traffic_fines" & early_type=="const")
print("traffic_fines_const:")
print(max(vec_traffic_linear$benefit_prefix))
print(min(vec_traffic_linear$benefit_prefix))


vec_traffic_linear <- subset(dt_merged2, dataset=="traffic_fines" & early_type=="nonmonotonic")
print("traffic_fines_nonmonotonic:")
print(max(vec_traffic_linear$benefit_prefix))
print(min(vec_traffic_linear$benefit_prefix))

vec_traffic_linear <- subset(dt_merged2, dataset=="bpic2017_cancelled" & early_type=="linear")
print("bpic2017_cancelled_linear:")
print(max(vec_traffic_linear$benefit_prefix))
print(min(vec_traffic_linear$benefit_prefix))

vec_traffic_linear <- subset(dt_merged2, dataset=="bpic2017_cancelled" & early_type=="const")
print("bpic2017_cancelled_const:")
print(max(vec_traffic_linear$benefit_prefix))
print(min(vec_traffic_linear$benefit_prefix))

vec_traffic_linear <- subset(dt_merged2, dataset=="bpic2017_cancelled" & early_type=="nonmonotonic")
print("bpic2017_cancelled_nonmonotonic:")
print(max(vec_traffic_linear$benefit_prefix))
print(min(vec_traffic_linear$benefit_prefix))

vec_traffic_linear <- subset(dt_merged2, dataset=="bpic2017_refused" & early_type=="linear")
print("bpic2017_refused_single:")
print(max(vec_traffic_linear$benefit_prefix))
print(min(vec_traffic_linear$benefit_prefix))

vec_traffic_linear <- subset(dt_merged2, dataset=="bpic2017_refused" & early_type=="const")
print("bpic2017_refused_const:")
print(max(vec_traffic_linear$benefit_prefix))
print(min(vec_traffic_linear$benefit_prefix))

vec_traffic_linear <- subset(dt_merged2, dataset=="bpic2017_refused" & early_type=="nonmonotonic")
print("bpic2017_refused_nonmonotonic:")
print(max(vec_traffic_linear$benefit_prefix))
print(min(vec_traffic_linear$benefit_prefix))


dt_merged2$benefit_prefix <- ifelse(dt_merged2$benefit_prefix < 0.9,0.9,dt_merged2$benefit_prefix)
dt_merged2$benefit_prefix <- ifelse(dt_merged2$benefit_prefix > 1.1,1.1,dt_merged2$benefit_prefix)


dt_merged_fire_delay_prefix$benefit_fire_delay <- ifelse(dt_merged_fire_delay_prefix$benefit_fire_delay < 0.75,0.75,dt_merged_fire_delay_prefix$benefit_fire_delay)
dt_merged_fire_delay_prefix$benefit_fire_delay <- ifelse(dt_merged_fire_delay_prefix$benefit_fire_delay > 1.25,1.25,dt_merged_fire_delay_prefix$benefit_fire_delay)

dt_merged_multi_fire_delay_prefix$benefit_fire_delay <- ifelse(dt_merged_multi_fire_delay_prefix$benefit_fire_delay < 0.75,0.75,dt_merged_multi_fire_delay_prefix$benefit_fire_delay)
dt_merged_multi_fire_delay_prefix$benefit_fire_delay <- ifelse(dt_merged_multi_fire_delay_prefix$benefit_fire_delay > 1.25,1.25,dt_merged_multi_fire_delay_prefix$benefit_fire_delay)


dt_merged_fire_delay$benefit_fscore <- ifelse(dt_merged_fire_delay$benefit_fscore < -0.5,0.5,dt_merged_fire_delay$benefit_fscore)
dt_merged_fire_delay$benefit_fscore <- ifelse(dt_merged_fire_delay$benefit_fscore > 0.5,0.5,dt_merged_fire_delay$benefit_fscore)


#print(dt_merged)


ggplot(subset(dt_merged, cls=="rf"), aes(factor(ratio_com_single), factor(ratio))) + geom_tile(aes(fill = benefit_min_prefix), colour = "black") + 
  theme_bw(base_size=base_size) + scale_fill_gradientn(colours=c("green","white","red"),breaks=c(0.9,1.0,1.1), limits=c(0.0,1.1),name="Correlation \n coefficient") + 
  xlab("c_com") + ylab("c_out : c_in") +  theme(axis.text.x = element_text(size=20))  + facet_wrap(dataset ~ early_type, ncol=3)
ggsave("/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/testresults/NonMyopic/result_heatmap_single_vs_minprefix.pdf", width = 20, height = 13)

ggplot(subset(dt_merged2, cls=="rf"), aes(factor(ratio_com_single), factor(ratio))) + geom_tile(aes(fill = benefit_prefix), colour = "black") + 
  theme_bw(base_size=base_size) + scale_fill_gradientn(colours=c("green4","green3","green2","green1","white","red1","red2","red3","red4"),breaks=c(0.9,1.0,1.1), limits=c(0.9,1.1), name="Ratio \n", labels=c(expression(phantom(x) <=0.9),"1.0",expression(phantom(x) >= 1.1)) ) + 
  xlab("c_com") + ylab("c_out : c_in") +  theme(axis.text.x = element_text(size=20))  + facet_wrap(dataset ~ early_type, ncol=3)
ggsave("/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/testresults/NonMyopic/result_heatmap_ratio_single_vs_prefix.pdf", width = 20, height = 13)

ggplot(subset(dt_merged2, cls=="rf"), aes(factor(ratio_com_single), factor(ratio))) + geom_tile(aes(fill = benefit_fixed), colour = "black") + 
  theme_bw(base_size=base_size) + scale_fill_gradientn(colours=c("red","white","green"),breaks=c(-0.8,0.0,0.8), limits=c(-1.0,1.0),name="Best System",labels=c("Single Threshold","Tie","Two Thresholds")) + 
  xlab("c_com") + ylab("c_out : c_in") +  theme(axis.text.x = element_text(size=20))  + facet_wrap(dataset ~ early_type, ncol=3)
ggsave("/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/testresults/NonMyopic/result_heatmap_single_vs_prefix_fixed.pdf", width = 20, height = 13)

ggplot(subset(dt_merged_fire_delay, cls=="rf"), aes(factor(ratio_com_single), factor(ratio))) + geom_tile(aes(fill = benefit_fire_delay), colour = "black") + 
  theme_bw(base_size=base_size) + scale_fill_gradientn(colours=c("green4","green3","green2","green1","white","red1","red2","red3","red4"),breaks=c(0.75,1.0,1.25), limits=c(0.6,1.4), name="Ratio \n", labels=c(expression(phantom(x) <=0.75),"1.0",expression(phantom(x) >= 1.25)) ) + 
  xlab("c_com") + ylab("c_out : c_in") +  theme(axis.text.x = element_text(size=20))  + facet_wrap(dataset ~ early_type, ncol=3)
ggsave("/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/testresults/NonMyopic/result_heatmap_ratio_immediatly_vs_fire_delay.pdf", width = 20, height = 13)

ggplot(subset(dt_merged_fire_delay_prefix, cls=="rf"), aes(factor(ratio_com_single), factor(ratio))) + geom_tile(aes(fill = benefit_fire_delay), colour = "black") + 
  theme_bw(base_size=base_size) + scale_fill_gradientn(colours=c("green4","green3","green2","green1","white","red1","red2","red3","red4"),breaks=c(0.75,1.0,1.25), limits=c(0.75,1.25), name="Ratio \n", labels=c(expression(phantom(x) <=0.75),"1.0",expression(phantom(x) >= 1.25)) ) + 
  xlab("c_com") + ylab("c_out : c_in") +  theme(axis.text.x = element_text(size=20))  + facet_wrap(dataset ~ early_type, ncol=3)
ggsave("/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/testresults/NonMyopic/result_heatmap_ratio_immediatly_vs_fire_delay_prefix.pdf", width = 20, height = 13)


ggplot(subset(dt_merged_multi_fire_delay_prefix, cls=="rf"), aes(factor(ratio_com_single), factor(ratio))) + geom_tile(aes(fill = benefit_fire_delay), colour = "black") + 
  theme_bw(base_size=base_size) + scale_fill_gradientn(colours=c("green4","green3","green2","green1","white","red1","red2","red3","red4"),breaks=c(0.75,1.0,1.25), limits=c(0.75,1.25), name="Ratio \n", labels=c(expression(phantom(x) <=0.75),"1.0",expression(phantom(x) >= 1.25)) ) + 
  xlab("c_com") + ylab("c_out : c_in") +  theme(axis.text.x = element_text(size=20))  + facet_wrap(dataset ~ early_type, ncol=3)
ggsave("/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/testresults/NonMyopic/result_heatmap_ratio_single_vs_multi_fire_delay_prefix.pdf", width = 20, height = 13)



ggplot(subset(dt_merged_fire_delay, cls=="rf"), aes(factor(ratio_com_single), factor(ratio))) + geom_tile(aes(fill = benefit_fscore), colour = "black") + 
  theme_bw(base_size=base_size) + scale_fill_gradientn(colours=c("red","white","green"),breaks=c(-0.5,0.0,0.5), limits=c(-0.5,0.5), name="fscore \n", labels=c(expression(phantom(x) <=-0.5),"0.0",expression(phantom(x) >= 0.5)) ) + 
  xlab("c_com") + ylab("c_out : c_in") +  theme(axis.text.x = element_text(size=20))  + facet_wrap(dataset ~ early_type, ncol=3)
ggsave("/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/testresults/NonMyopic/result_heatmap_fscore_immediatly_vs_fire_delay.pdf", width = 20, height = 13)


