library( boot )

c_strSite	<- "STSite"
c_strPerc	<- "Percent.of.Human.Reads"

funcRegress <- function( frmeIn ) {
	
	adPerc <- frmeIn[,c_strPerc]
	for( strSite in levels( frmeIn[,c_strSite] ) ) {
		afCur <- frmeIn[,c_strSite] == strSite
		adPerc[afCur & is.na( adPerc )] <- median( adPerc[afCur], na.rm = TRUE ) }
	for( iCol in 2:ncol( frmeIn ) ) {
		strCol <- colnames( frmeIn )[iCol]
		if( strCol %in% c(c_strSite, c_strPerc) ) {
			next }
		if( !( iCol %% 500 ) ) {
			write( c(iCol, ncol( frmeIn )), stderr( ) ) }
#		lmod <- glm( frmeIn[,iCol] ~ frmeIn[,c_strSite] + frmeIn[,c_strPerc], family = binomial )
#		frmeIn[,iCol] <- inv.logit( logit( frmeIn[,iCol] ) - ( adPerc * lmod$coef["frmeIn[, c_strPerc]"] ) ) }
		lmod <- glm( frmeIn[,iCol] ~ frmeIn[,c_strSite] + frmeIn[,c_strPerc], family = quasipoisson )
		print( strCol )
		print( lmod )
		print( summary( lmod ) )
		frmeIn[,iCol] <- exp( log( frmeIn[,iCol] ) - ( adPerc * lmod$coef["frmeIn[, c_strPerc]"] ) ) }
	return( frmeIn )
}

funcRegress2 <- function( frmeIn ) {

	astrSites <- levels( frmeIn[,c_strSite] )
	if( !length( astrSites ) ) {
		return( frmeIn ) }
	aiCols <- setdiff( which( !( colnames( frmeIn ) %in% c(c_strSite, c_strPerc) ) ), 1 )
	for( strSite in astrSites ) {
		write( strSite, stderr( ) )
		aiSite <- which( frmeIn[,c_strSite] == strSite )
		adPerc <- frmeIn[aiSite, c_strPerc]
		adPerc[is.na( adPerc )] <- median( adPerc, na.rm = TRUE )
		if( length( adPerc ) < 4 ) {
			next }
		for( iCol in aiCols ) {
			lmod <- glm( frmeIn[aiSite, iCol] ~ frmeIn[aiSite, c_strPerc], family = poisson )
			frmeIn[aiSite, iCol] <- exp( log( frmeIn[aiSite, iCol] ) - ( adPerc * lmod$coef["frmeIn[aiSite, c_strPerc]"] ) ) } }
	frmeIn[,aiCols] <- frmeIn[,aiCols] / rowSums( frmeIn[,aiCols], na.rm = TRUE )
	return( frmeIn )
}

frmeIn <- read.delim( file( "stdin" ), row.names = 1 )
frmeOut <- funcRegress( frmeIn )
print( "DONE" )
write.table( frmeOut, stdout( ), quote = FALSE, sep = "\t", na = "", col.names = NA )
