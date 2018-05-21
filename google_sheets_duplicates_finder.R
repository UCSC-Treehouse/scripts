# Check for duplicates in Google Sheets


# Import necessary libraries
library(tidyverse)

#First make sure you have correctly downloaded your Google Sheets files
#On the correct sheet, go to File>Download as>Comma-separated values

#With the files in your Downloads folder
setwd("~/Downloads")

curated_mutations = read.csv("TreehouseSamples_Mutation-Fusion-Clinical - CuratedMutations.csv")
pending_mutations = read.csv("TreehouseSamples_Mutation-Fusion-Clinical - PendingCuration.csv")

joined_mutations <- bind_rows(curated_mutations, pending_mutations)
duplicate_mutations <- joined_mutations[duplicated(joined_mutations[c(1:3,5)]) | duplicated(joined_mutations[c(1:3,5)], fromLast = TRUE), ]
nrow(duplicate_mutations)
