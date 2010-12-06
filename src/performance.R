library( ROCR )

funcAcc <- function( adX, adY ) {

	if( is.null( adX ) || is.null( adY ) ) {
		return( 0 ) }
	return( cor( adX, adY ) ) }

funcClean <- function( frmeData ) {
	iCol <- 2

	iRow <- 1
	for( i in 1:nrow( frmeData ) ) {
		if( !is.na( frmeData[i, iCol] ) ) {
			iRow <- i
			break } }
	astrRows <- rownames( frmeData )[iRow:nrow( frmeData )]
	astrCols <- colnames( frmeData )[iCol:ncol( frmeData )]
	frmeData <- data.frame( frmeData[iRow:nrow( frmeData ), iCol:ncol( frmeData )] )
	rownames( frmeData ) <- astrRows
	colnames( frmeData ) <- astrCols
	for( i in 1:ncol( frmeData ) ) {
		frmeData[,i] <- type.convert( as.character( frmeData[,i] ) ) }
	frmeData[is.na( frmeData )] <- 0
	if( ncol( frmeData ) > 1 ) {
		aiDitch <- c()
		for( iCol in 2:ncol( frmeData ) ) {
			if( max( frmeData[,iCol] ) == 0 ) {
				aiDitch <- c(aiDitch, iCol) } }
		frmeData <- frmeData[,setdiff( 1:ncol( frmeData ), aiDitch )] }
	
	return( frmeData ) }

funcData <- function( strCov, strAbd ) {
	
	frmeCov <- read.delim( strCov, row.names = 1 )
	frmeAbd <- read.delim( strAbd, row.names = 1 )
	frmeCov <- funcClean( frmeCov )
	frmeAbd <- funcClean( frmeAbd )
	
	return( list( abd = frmeAbd, cov = frmeCov ) ) }

funcAUC <- function( pPred ) {

	if( is.na( pPred ) ) {
		return( 0 ) }
	pPerf <- performance( pPred, "auc", fpr.stop = c_dFPR )
	return( pPerf@y.values[1][[1]] / c_dFPR ) }

funcPlotAbd <- function( adRMSE, astrCom ) {

	afRMSE <- adRMSE > 0
	adRMSE <- adRMSE[afRMSE]
	astrCom <- astrCom[afRMSE]
	if( !length( adRMSE ) ) {
		adRMSE <- c(0)
		astrCom <- c("") }

	par( mar = c(12, 4, 4, 11) + 0.1 )
	dMin <- min( adRMSE ) * 0.99
	adX <- barplot( adRMSE, ylim = c(dMin, max( adRMSE ) * 1.01), xpd = FALSE,
		ylab = "Cor.", main = "Abundance" )
	text( adX, dMin * 0.999, astrCom, xpd = TRUE, srt = -45, adj = 0 ) }

funcPlotAbdFact <- function( adRMSE, astrCom, strFact, strName ) {
	
	aiIn <- c()
	for( i in 1:length( astrCom ) ) {
		if( length( grep( strFact, astrCom[i] ) ) ) {
			aiIn <- c(aiIn, i) } }
	aiOut <- setdiff( 1:length( astrCom ), aiIn )
	adAve <- c(mean( adRMSE[aiIn] ), mean( adRMSE[aiOut] ))
	adStd <- c(sd( adRMSE[aiIn] ), sd( adRMSE[aiOut] ))
	adStd <- adStd * ( max( adAve ) - min( adAve ) ) / mean( adStd )
	dStd <- max( adStd )
	dMin <- ( min( adAve ) - dStd ) * 0.99
	adX <- barplot( adAve, ylim = c(dMin, ( max( adAve ) + dStd ) * 1.01), xpd = FALSE,
		ylab = "Cor.", main = strName )
	errbar( adX, adAve, adAve + adStd, adAve - adStd, add = TRUE )
	text( adX, dMin * 0.999, c(strName, paste( "~", strName, sep = "" )), xpd = TRUE, srt = -45, adj = 0) }

funcPlotCovFact <- function( lsPred, astrCom, strFact, strName ) {
	
	aiIn <- c()
	adAUC <- c()
	for( i in 1:length( astrCom ) ) {
		adAUC <- c(adAUC, funcAUC( lsPred[[i]] ))
		if( length( grep( strFact, astrCom[i] ) ) ) {
			aiIn <- c(aiIn, i) } }
	aiOut <- setdiff( 1:length( astrCom ), aiIn )
	adAve <- c(mean( adAUC[aiIn] ), mean( adAUC[aiOut] ))
	adStd <- c(sd( adAUC[aiIn] ), sd( adAUC[aiOut] ))
	adStd <- adStd * ( max( adAve ) - min( adAve ) ) / mean( adStd )
	if( !length( adAve ) ) {
		adAve <- c(0)
		adStd <- c(0) }
	dStd <- max( adStd )
	dMin <- ( min( adAve ) - dStd ) * 0.99
	adX <- barplot( adAve, ylim = c(dMin, ( max( adAve ) + dStd ) * 1.01), xpd = FALSE,
		ylab = sprintf( "pAUC %g", c_dFPR ), main = strName )
	errbar( adX, adAve, adAve + adStd, adAve - adStd, add = TRUE )
	text( adX, dMin * 0.999, c(strName, paste( "~", strName, sep = "" )), xpd = TRUE, srt = -45, adj = 0) }

funcPerfs <- function( lsPred ) {

	lsPerf <- lsPred
	if( length( lsPerf ) ) {
		for( i in 1:length( lsPerf ) ) {
			if( is.na( lsPerf[[i]] ) ) {
				pCur <- 0 }
			else {
				pCur <- performance( lsPerf[[i]], "tpr", "fpr" ) }
			lsPerf[[i]] <- pCur } }
	return( lsPerf ) }
	
funcPlotCov <- function( lsPred, astrCom ) {
	
	#roc.plot( adGSCov, frmeCov[,astrCom], legend = TRUE, show.thres = FALSE, leg.text = astrCom, thresholds = seq( 0, 1, 0.01 ) )
	lsPerf <- funcPerfs( lsPred )
	aiOK <- c()
	if( length( lsPerf ) ) {
		for( i in 1:length( lsPerf ) ) {
			if( class( lsPerf[[i]] ) == "performance" ) {
				aiOK <- c(aiOK, i) } }
		lsPerf <- lsPerf[aiOK] }
	if( !length( lsPerf ) ) {
		plot( 0 )
		return( ) }
	plot( lsPerf[[1]], lty = 0, main = sprintf( "Coverage (pAUC %g, rand = %g)", c_dFPR, c_dFPR / 2 ) )
	for( i in 1:length( lsPerf ) ) {
		plot( lsPerf[[i]], lwd = 2, add = TRUE, col = ( i %% 8 ) + 1, lty = ( i %% 3 ) + 1 ) }
	aiCol = ( 1:length( lsPerf ) %% 8 ) + 1
	aiLty = ( 1:length( lsPerf ) %% 3 ) + 1
	astrNames <- astrCom
	for( i in aiOK ) {
		d <- funcAUC( lsPred[[i]] )
		astrNames[i] <- paste( astrCom[i], " (", sprintf( "%0.4f", d ), ")", sep = "" ) }
	astrNames <- astrNames[aiOK]
	legend( "bottomright", astrNames, col = aiCol, lty = aiLty, lwd = 2 ) }

funcPlotCovAUC <- function( lsPred, astrCom ) {
	
	adAUC <- c()
	lsPerf <- funcPerfs( lsPred )
	if( length( lsPerf ) ) {
		for( i in 1:length( lsPerf ) ) {
			adAUC <- c(adAUC, funcAUC( lsPred[[i]] )) } }
	
	afAUC <- adAUC > ( 1.001 * c_dFPR / 2 )
	adAUC <- adAUC[afAUC]
	astrCom <- astrCom[afAUC]
	if( !length( adAUC ) ) {
		adAUC <- c(0)
		astrCom <- c("") }
	
	par( mar = c(14, 4, 4, 11) + 0.1 )
	dMin <- min( adAUC ) * 0.99
	adX <- barplot( adAUC, ylim = c(dMin, max( adAUC ) * 1.01), xpd = FALSE,
		ylab = "pAUC", main = sprintf( "Coverage (pAUC %g)", c_dFPR ) )
	text( adX, dMin * 0.999, astrCom, xpd = TRUE, srt = -45, adj = 0 ) }

funcBase <- function( lsData, astrIn = c(), astrOut = c() ) {

	frmeAbd <- lsData$abd
	frmeCov <- lsData$cov
	strBase <- colnames( frmeAbd )[1]
	strTag <- sub( "^[^_]+_mock", "mock", strBase )
	adGSCov <- frmeCov[,strBase]
	adGSAbd <- frmeAbd[,strBase]
	astrPCov <- rownames( frmeCov )
	astrPAbd <- rownames( frmeAbd )
	astrCom <- c()
	adRMSE <- c()
	lsPred <- list()
	astrCols <- sort( union( colnames( frmeCov ), colnames( frmeAbd ) ) )
	for( strCom in astrCols ) {
		if( ( strCom == strBase ) || !length( grep( strTag, strCom ) ) ) {
			next }
		fOK <- TRUE
		if( length( astrOut ) && ( strCom %in% astrOut ) ) {
			fOK <- FALSE }
		if( length( astrIn ) && !( strCom %in% astrIn ) ) {
			fOK <- FALSE }
		if( !fOK ) {
			next }
#if( !length( grep( "mp[tm]", strCom ) ) ) {
#	next }
#if( !length( grep( "annodb", strCom ) ) ) {
#	next }
#if( length( grep( "wbl", strCom ) ) ) {
#	next }
#if( length( grep( "mpt\\.[a-z]{3}\\.[a-z]{3}\\.xpe", strCom ) ) ) {
#	next }
#if( length( grep( "nul$", strCom ) ) ) {
#	next }
#if( !length( grep( "(?:P30E1)|(?:annodb)", strCom ) ) ) {
#	next }
		astrCom <- c(astrCom, sub( "_vs_All_annodb", "_mbx", sub( "mock_", "",
			sub( ".alignments", "", strCom ) ) ))

		if( length( grep( "mtc", strCom ) ) ) {
			aiAbd <- setdiff( 1:length( astrPAbd ), grep( '^((ko)|M|K)[0-9]+$', astrPAbd ) )
			aiCov <- setdiff( 1:length( astrPCov ), grep( '^((ko)|M|K)[0-9]+$', astrPCov ) )
		} else if( length( grep( "mpm", strCom ) ) ) {
			aiAbd <- grep( '^(M|K)[0-9]+$', astrPAbd )
			aiCov <- grep( '^(M|K)[0-9]+$', astrPCov )
		} else {
			aiAbd <- grep( '^((ko)|K)[0-9]+$', astrPAbd )
			aiCov <- grep( '^((ko)|K)[0-9]+$', astrPCov ) }
		
		if( ( strCom %in% colnames( frmeAbd ) ) && ( max( adGSAbd[aiAbd] ) > 0 ) ) {
			dCur <- funcAcc( adGSAbd[aiAbd] / sum( adGSAbd[aiAbd] ), frmeAbd[aiAbd, strCom] )
		} else {
			dCur <- 0 }
		adRMSE <- c(adRMSE, dCur)
		pCur <- NA
		if( ( strCom %in% colnames( frmeCov ) ) && ( max( adGSCov[aiCov] ) > 0 ) ) {
			try( pCur <- prediction( frmeCov[aiCov, strCom], adGSCov[aiCov] ) ) }
		if( is.na( pCur ) || ( class( pCur ) == "try-error" ) ) {
			pCur <- prediction( c(0, 1, 0, 1), c(0, 0, 1, 1) ) }
		lsPred <- c(lsPred, pCur) }
	return( list( names = astrCom, rmse = adRMSE, pred = lsPred ) ) }

funcScatter <- function( lsData, strTarget ) {

	frmeAbd <- lsData$abd
	astrPaths <- c()
	for( strPath in rownames( frmeAbd ) ) {
		fOK <- TRUE
		if( !length( grep( 'mtc', strTarget ) ) == !length( grep( '^((ko)|M|K)[0-9]+$', strPath ) ) ) {
			fOK <- FALSE }
		if( !!length( grep( 'mpm', strTarget ) ) == !length( grep( '^M[0-9]+$', strPath ) ) ) {
			fOK <- FALSE }
		if( fOK ) {
			astrPaths <- c(strPath, astrPaths) } }

	strBase <- colnames( frmeAbd )[1]
	adGSAbd <- frmeAbd[astrPaths, strBase] / max( 1e-10, sum( frmeAbd[astrPaths, strBase] ) )
	adX <- frmeAbd[astrPaths, strTarget]
	ad <- c(adX, adGSAbd)
	if( length( adX ) ) {
		dMin <- min( ad )
		dMax <- max( ad ) }
	else {
		adGSAbd <- c()
		dMin <- 0
		dMax <- 0 }
	adLim <- c(0.99 * dMin, 1.01 * dMax)
	plot( adX, adGSAbd, xlim = adLim, ylim = adLim, xlab = sprintf( "Predicted (r = %0.4f)",
		funcAcc( adX, adGSAbd ) ), ylab = "Actual", main = "Abundance", pch = "o" )
	if( length( adX ) ) {
		lmod <- lm( adGSAbd ~ adX )
		abline( reg = lmod )
		abline( 0, 1, lwd = 2 ) } }

funcSAUC <- function( lsData, iCol ) {

	funcScatter( lsData, colnames( lsData$abd )[iCol + 1] )
	lsBase <- funcBase( lsData, c(colnames( lsData$cov )[iCol + 1]) )
	funcPlotCov( lsBase$pred, lsBase$names ) }
	
funcPathways <- function( strFile ) {
	
	lsRet <- list()
	for( strLine in readLines( strFile ) ) {
		astrLine <- strsplit( strLine, "\t" )[[1]]
		lsRet[astrLine[1]] <- list(astrLine[2:length( astrLine )]) }
	
	return( lsRet ) }

c_iWidth	<- 4
c_iHeight	<- 4
c_dFPR		<- 0.1

strOutput		<- "output/mock_stg_hc_04.pdf"
strCoverage		<- "output/mock_stg_hc_04a.txt"
strAbundance	<- ""
astrArgs <- commandArgs( TRUE )
if( length( astrArgs ) >= 1 ) {
	strOutput <- astrArgs[1] }
if( length( astrArgs ) >= 2 ) {
	strCoverage <- astrArgs[2] }
if( length( astrArgs ) >= 3 ) {
	strAbundance <- astrArgs[3] }
if( !nchar( strAbundance ) ) {
	strAbundance <- strCoverage }

lsData <- funcData( strCoverage, strAbundance )
iTypes <- min( 5000, max( ncol( lsData$abd ), ncol( lsData$cov ) ) - 1 )
if( !is.finite( iTypes ) ) {
	iTypes <- 0 }

fPDF <- length( grep( "\\.pdf$", strOutput ) )
iWidth <- 1 + ( iTypes / 10 )
if( fPDF ) {
	pdf( strOutput, width = 2 * iWidth * c_iWidth, height = c_iHeight * ( 1 + iTypes ) )
} else {
	png( strOutput, units = "in", res = 160, width = 2 * ( iWidth + c_iWidth ), height = c_iHeight * ( 1 + iTypes ) ) }
par( mfrow = c(1 + iTypes, 2) )
lsBase <- funcBase( lsData )
funcPlotAbd( lsBase$rmse, lsBase$names )
funcPlotCovAUC( lsBase$pred, lsBase$names )
par( mar = c(5, 4, 4, 2) + 0.1 )
for( iType in 1:iTypes ) {
	funcSAUC( lsData, iType ) }
dev.off( )
