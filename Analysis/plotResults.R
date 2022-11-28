library( ggplot2 )
library( reshape )

baseDirectory <- "/Users/ntustison/Data/Public/BRATS/RegistrationCompetition2022/Analysis/"

resultsAffine <- read.csv( paste0( baseDirectory, "resultsAffine.csv" ) )
resultsSyNQuick <- read.csv( paste0( baseDirectory, "resultsSyNQuick.csv" ) )
resultsUniSyN <- read.csv( paste0( baseDirectory, "resultsUnivariateSyN.csv" ) )
resultsMultiSyN <- read.csv( paste0( baseDirectory, "resultsMultivariateSyN.csv" ) )
results <- rbind( resultsAffine, resultsSyNQuick, resultsUniSyN, resultsMultiSyN )


# transformTypes <- unique( resultsUniSyN$RegistrationType )
# modalities <- unique( resultsUniSyN$Modalities )
# subjects <- unique( resultsUniSyN$Subject )
# for( i in seq.int( length( subjects ) ) )
#   {
#   for( j in seq.int( length( transformTypes ) ) )
#     {
#     for( k in seq.int( length( modalities ) ) )
#       {
#       numberOfEntries <- length( which( resultsUniSyN$Subject == subjects[i] &
#                                         resultsUniSyN$RegistrationType == transformTypes[j] & 
#                                         resultsUniSyN$Modalities == modalities[k] ) )
#       if( numberOfEntries != 1 )
#          {
#          cat( subjects[i], ", ", transformTypes[j], ", ", modalities[k], ": ", numberOfEntries, "\n")
#          }
#       } 
#     }
#   }

results$Accuracy <- 1.0 - results$PostLandmarkError / results$PreLandmarkError

transformTypes <- unique( results$RegistrationType )
modalities <- unique( results$Modalities )

performanceMap <- array( data = NA, dim = c( length( transformTypes ), length( modalities ) ) )
rownames( performanceMap ) <- transformTypes
colnames( performanceMap ) <- modalities

timing <- rep( 0, length( transformTypes ) )
timingSingleModality <- rep( 0, length( transformTypes ) )
timingTwoModalities <- rep( 0, length( transformTypes ) )

for( i in seq.int( length( transformTypes ) ) ) 
  {
  timing[i] <- mean( results$TimeElapsed[which( results$RegistrationType == transformTypes[i] )])
  timingSingleModality[i] <- mean( results$TimeElapsed[which( results$RegistrationType == transformTypes[i] & 
                                                              results$Modalities %in% c( "t1", "t1ce", "flair", "t2" ) )])
  timingTwoModalities[i] <- mean( results$TimeElapsed[which( results$RegistrationType == transformTypes[i] & 
                                                              results$Modalities %in% c( "t1ce_t2", "t1ce_flair" ) )])
  for( j in seq.int( length( modalities ) ) )
    {
    # performanceMap[i, j] <- mean( results$Accuracy[which( results$RegistrationType == transformTypes[i] & results$Modalities == modalities[j] )])
    performanceMap[i, j] <- median( results$Accuracy[which( results$RegistrationType == transformTypes[i] & results$Modalities == modalities[j] )])
    }
  }
  
performanceMelt <- melt( performanceMap )
colnames( performanceMelt ) <- c( "TransformType", "Modality", "AccuracyImprovement" )
performanceMelt$TransformType <- factor( performanceMelt$TransformType, 
    levels = c( "antsRegistrationSyNQuick[a]", 
                "antsRegistrationSyNQuick[s,32]", "antsRegistrationSyNQuick[b,32,26]",                 
                "antsRegistrationSyN[s,4]", "antsRegistrationSyN[b,4,26]", 
                "antsRegistrationSyN[s,2]", "antsRegistrationSyN[b,2,26]", "brats" )  
    )
performanceMelt$Modality <- factor( performanceMelt$Modality, 
    levels = c( "t1", "t1ce", "flair", "t2", "t1ce_flair", "t1ce_t2" ) )

heatMapPlot <- ggplot( data = performanceMelt, aes( x = TransformType, y = Modality ) ) + 
               geom_tile( aes( fill = AccuracyImprovement ) ) + 
               geom_text( aes( label = round( AccuracyImprovement, 2 ) ) ) +
               theme( axis.text.x = element_text( angle = 90, hjust = 1, vjust = 0.5 ) )
ggsave( paste0( baseDirectory, "/accuracy.pdf" ), heatMapPlot, width = 7, height = 5 )

results$RegistrationType <- factor( results$RegistrationType, 
    levels = c( "antsRegistrationSyNQuick[a]", 
                "antsRegistrationSyNQuick[s,32]", "antsRegistrationSyNQuick[b,32,26]",                 
                "antsRegistrationSyN[s,4]", "antsRegistrationSyN[b,4,26]", 
                "antsRegistrationSyN[s,2]", "antsRegistrationSyN[b,2,26]", "brats" )  
    )
barPlot <- ggplot( data = results )   + 
           geom_boxplot( aes( x = RegistrationType, y = Accuracy, fill = Modalities ) ) +
           theme( axis.text.x = element_text( angle = 90, hjust = 1, vjust = 0.5 ) )
           
ggsave( paste0( baseDirectory, "/accuracyBox.pdf" ), barPlot, width = 7, height = 5 )
