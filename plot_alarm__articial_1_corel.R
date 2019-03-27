library(ggplot2)
library(plyr)
library(RColorBrewer)
library(reshape2)

setwd("/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/OutputArtificialEvalSingleCorel/")
files <- list.files()
data <- data.frame()
for (file in files) {
  tmp <- read.table(file, sep=";", header=T)
  tmp$cls <- "rf"
  data <- rbind(data, tmp)
}

data$ratio <- paste(data$c_miss, data$c_action, sep=":")

base_size <- 36
line_size <- 1
point_size <- 4

data <- subset(data, dataset != "bpic2018")
data <- subset(data, dataset != "uwv")
data$dataset <- as.character(data$dataset)
data$dataset[data$dataset=="uwv_all"] <- "uwv"
data$dataset[data$dataset=="bpic2017_cancelled"] <- "bpic2017"
data$dataset[data$dataset=="traffic_fines_1"] <- "traffic_fines"

#data <- subset(data, cls=="rf")
#print(subset(data,method=="perfect_prediction"))

head(data)

data$ratio <- as.factor(data$ratio)
#print(data$ratio)
#data$ratio <- factor(data$ratio, levels(data$ratio)[c(1,3,5,6,2,4)])
#print(data$ratio)
data$ratio_com <- as.factor(data$c_com)
#data$ratio_com <- factor(data$ratio_com, levels(data$ratio_com)[c(1,13,10,2,14,12,11,3,5,7,9,4,6,8)])
#print(data$ratio_com)

ggplot(subset(data, cls=="rf"), aes(factor(ratio_com), factor(ratio))) + geom_tile(aes(fill = value), colour = "black") + 
  theme_bw(base_size=base_size) + scale_fill_gradientn(colours=c("red","white","green"),breaks=c(-0.5,0,0.5), limits=c(-1,1),name="Correlation \n coefficient") + 
  xlab("c_com") + ylab("c_out : c_in") +  theme(axis.text.x = element_text(size=20))  + facet_wrap(dataset ~ early_type, ncol=3)
ggsave("/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/testresults/artificialClassifiers/result_heatmap_corel.pdf", width = 20, height = 10)
