library(ggplot2)
setwd("/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/rf_eval_results/")

setEPS()
postscript("/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/testresults/hello_world2.eps", width=13, height=4)
vector1 <- c(0,3,4)
vector2 <- c(1,2,3)
data <- data.frame(vector1,vector2)
print(data)
ggplot(data,aes(x=vector1, y=vector2)) +
  geom_boxplot()
#ggsave("/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/testresults/hello_world2.pdf")
dev.off()