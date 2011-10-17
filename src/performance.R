library( gplots )
library( ROCR )

funcAcc <- function( adX, adY ) {

	if( is.null( adX ) || is.null( adY ) ) {
		return( 0 ) }
	return( cor( adX, adY ) ) }

funcTrans <- function( adX ) {

	if( is.null( adX ) ) {
		return( 0 ) }
	return( asin( sqrt( adX ) ) ) }

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

funcPlotAbd <- function( adRMSE, astrCom, strTitle ) {

	afRMSE <- adRMSE > 0
	adRMSE <- adRMSE[afRMSE]
	astrCom <- astrCom[afRMSE]
	if( !length( adRMSE ) ) {
		adRMSE <- c(0)
		astrCom <- c("") }

	dMin <- min( adRMSE ) * 0.99
	adX <- barplot( adRMSE, ylim = c(dMin, max( adRMSE ) * 1.01), xpd = FALSE,
		ylab = "Correlation", main = sprintf( "Abundance (%s, asin sqrt)", strTitle ) )
	text( adX, dMin * 0.995, astrCom, xpd = TRUE, srt = -45, adj = 0 ) }

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

funcPlotCovAUC <- function( lsPred, astrCom, strTitle ) {
	
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
	
	dMin <- min( adAUC ) * 0.99
	adX <- barplot( adAUC, ylim = c(dMin, max( adAUC ) * 1.01), xpd = FALSE,
		ylab = "pAUC", main = sprintf( "Coverage (%s, pAUC %g)", strTitle, c_dFPR ) )
	text( adX, dMin * 0.995, astrCom, xpd = TRUE, srt = -45, adj = 0 ) }

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
		strName <- sub( "_vs_All_annodb", "_mbx", sub( "mock_", "", sub( ".alignments", "", strCom ) ) )
#		strName <- sub( "stg", "Stg.", strName )
#		strName <- sub( "even", "Even", strName )
#		strName <- sub( "hc_", "HC", strName )
#		strName <- sub( "lc_", "LC", strName )
		strName <- sub( "((stg)|(even))_[hl]c_", "", strName )
		strName <- sub( "mbx.", "", strName )
		strName <- sub( "htc.", "", strName )
		strName <- sub( "keg.", "", strName )
		strName <- sub( "(mp[mt]..{7}).nae", "\\1 +GFAve", strName )
		strName <- sub( "(mp[mt]..{7}).nve", "\\1 +GF", strName )
		strName <- sub( "(mp[mt]..{7}).nul", "\\1 -GF", strName )
		strName <- sub( "(mp[mt]..{3}).wbl", "\\1 +SmWB", strName )
		strName <- sub( "(mp[mt]..{3}).nve", "\\1 +Sm", strName )
		strName <- sub( "(mp[mt]..{3}).nul", "\\1 -Sm", strName )
		strName <- sub( "(mp[mt]).cop", "\\1 +TaxC#", strName )
		strName <- sub( "(mp[mt]).nve", "\\1 +Tax", strName )
		strName <- sub( "(mp[mt]).nul", "\\1 -Tax", strName )
		strName <- sub( "mpm", "Mod.", strName )
		strName <- sub( "mpt", "Path", strName )
		strName <- sub( "keg", "KOs", strName )
		strName <- sub( "ksb", "KOs, bitscore", strName )
		strName <- sub( "kie", "KOs, inv. E", strName )
		strName <- sub( "ksg", "KOs, sigm. E", strName )
		strName <- sub( ".nul.((nve)|(nul))(.xpe)?$", "", strName )
		strName <- sub( "nve.nve.nul.nul.nul$", "-All BBH", strName )
		strName <- sub( "nve$", "BBH", strName )
		strName <- gsub( "_", " ", strName )
#		print(strName)
		astrCom <- c(astrCom, strName)
		
		aiAbd <- which( apply( t(astrPAbd), 2, function( s ) { return( funcGrepRow( strCom, s ) ) } ) )
		aiCov <- which( apply( t(astrPCov), 2, function( s ) { return( funcGrepRow( strCom, s ) ) } ) )
		
		if( ( strCom %in% colnames( frmeAbd ) ) && ( max( adGSAbd[aiAbd] ) > 0 ) ) {
			adX <- funcTrans( adGSAbd[aiAbd] / sum( adGSAbd[aiAbd] ) )
			adY <- funcTrans( frmeAbd[aiAbd, strCom] )
			dCur <- funcAcc( adX, adY )
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

funcGrepRow <- function( strBase, strRow ) {
	
	if( length( grep( "mtc", strBase ) ) ) {
		fRet <- !length( grep( '^((ko)|M|K)[0-9]+$', strRow ) )
	} else if( length( grep( "mpt", strBase ) ) ) {
		fRet <- length( grep( "^((ko)|K)[0-9]+$", strRow ) )
	} else {
		fRet <- length( grep( "^(M|K)[0-9]+$", strRow ) ) }
	return( !!fRet ) }
	
funcScatter <- function( lsData, strTarget, strName ) {

	frmeAbd <- lsData$abd
	aiPaths <- which( apply( t(rownames( frmeAbd )), 2, function( s ) { return( funcGrepRow( strTarget, s ) ) } ) )
	strBase <- colnames( frmeAbd )[1]
	adGSAbd <- frmeAbd[aiPaths, strBase] / max( 1e-10, sum( frmeAbd[aiPaths, strBase] ) )
	adX <- frmeAbd[aiPaths, strTarget]
	if( is.null( adGSAbd ) || is.null( adX ) ) {
		adGSAbd <- NULL
		adX <- NULL }
	else {
		adGSAbd <- funcTrans( adGSAbd )
		adX <- funcTrans( adX )
		afNA <- is.na( adGSAbd ) | is.na( adX )
		adGSAbd <- adGSAbd[!afNA]
		adX <- adX[!afNA] }

	ad <- c(adX, adGSAbd)
	if( length( adX ) ) {
		dMin <- min( ad )
		dMax <- max( ad ) }
	else {
		adGSAbd <- c()
		dMin <- 0
		dMax <- 0 }
	adLim <- c(0.99 * dMin, 1.01 * dMax)
	if( length( adX ) > 1000 ) {
		func <- sunflowerplot
		lsHist <- hist2d( adX, adGSAbd, nbins = 20, show = FALSE )
		adCounts <- as.numeric( lsHist$counts )
		adCounts <- sapply( adCounts, function( d ) { min( d, 25 ) } )
		adPY <- c()
		for( i in 1:length( lsHist$y ) ) {
			adPY <- c(adPY, rep( lsHist$y[i], length( lsHist$x ) )) }
		adPX <- rep( lsHist$x, length( lsHist$y ) ) }
	else {
		func <- plot
		adPX <- adX
		adPY <- adGSAbd
		adCounts <- NULL }
	func( adPX, adPY, xlim = adLim, ylim = adLim, xlab = sprintf( "Predicted (r = %0.4f)",
		funcAcc( adX, adGSAbd ) ), ylab = "Actual", pch = "o",
		number = adCounts, seg.col = "black", size = 0.03, seg.lwd = 0.8,
		main = sprintf( "Abd. (%s, asin sqrt)", strName ) )
	if( length( adX ) ) {
		lmod <- lm( adGSAbd ~ adX )
		abline( reg = lmod )
		abline( 0, 1, lwd = 2 ) } }

funcSAUC <- function( lsData, iCol ) {

	lsBase <- funcBase( lsData, c(colnames( lsData$cov )[iCol + 1]) )
	funcScatter( lsData, colnames( lsData$abd )[iCol + 1], lsBase$names[1] )
	funcPlotCov( lsBase$pred, lsBase$names ) }
	
funcTitle <- function( strFile ) {
	
	strRet <- ""
	if( length( grep( "even", strFile ) ) ) {
		strRet <- "Even" }
	if( length( grep( "stg", strFile ) ) ) {
		strRet <- "Stg." }
	if( length( grep( "hc", strFile ) ) ) {
		strRet <- sprintf( "%s %s", strRet, "HC" ) }
	if( length( grep( "lc", strFile ) ) ) {
		strRet <- sprintf( "%s %s", strRet, "LC" ) }
	if( !nchar( strRet ) ) {
		strRet <- sub( "\\.\\S+$", strFile ) }
	return( strRet ) }

c_iWidth	<- 2.75
c_iHeight	<- 2.5
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
iWidth <- 1 + ( iTypes / 30 )
if( fPDF ) {
	pdf( strOutput, width = 2 * iWidth * c_iWidth, height = c_iHeight * ( 1 + iTypes ) )
} else {
	png( strOutput, units = "in", res = 160, width = 2 * iWidth * c_iWidth, height = c_iHeight * ( 1 + iTypes ) ) }
par( mfrow = c(1 + iTypes, 2) )
lsBase <- funcBase( lsData )
par( mar = c(6.5, 4, 3, 2.25) + 0.1 )
strTitle <- funcTitle( strOutput )
funcPlotAbd( lsBase$rmse, lsBase$names, strTitle )
funcPlotCovAUC( lsBase$pred, lsBase$names, strTitle )
par( mar = c(4, 4, 3, 1) + 0.1 )
for( iType in 1:iTypes ) {
	funcSAUC( lsData, iType ) }
dev.off( )
