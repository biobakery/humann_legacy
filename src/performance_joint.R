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
	
funcPlotCov <- function( lsPred, astrNames ) {
	c_aiLines	<- 1:10
	
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
	plot( lsPerf[[1]], lty = 0, main = sprintf( "Coverage", c_dFPR, c_dFPR / 2 ), xlim = c(0, c_dFPR) )
	for( i in 1:length( lsPerf ) ) {
		plot( lsPerf[[i]], lwd = 2, add = TRUE, lty = c_aiLines[( ( i - 1 ) %% length( c_aiLines ) ) + 1] ) }
	aiCol = ( 1:length( lsPerf ) %% 8 ) + 1
	aiLty = ( 1:length( lsPerf ) %% 3 ) + 1
	for( i in aiOK ) {
		d <- funcAUC( lsPred[[i]] )
		astrNames[i] <- paste( astrNames[i], sprintf( ", pAUC(%g)=%0.2f", c_dFPR, d ), sep = "" ) }
	astrNames <- astrNames[aiOK]
	legend( "bottomright", astrNames, lwd = 2, lty = c_aiLines ) }

funcBase <- function( lsData, astrTargets ) {

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
	for( strTarget in astrTargets ) {
		fHit <- FALSE
		for( strOne in colnames( frmeAbd ) ) {
			if( length( grep( strTarget, strOne ) ) ) {
				fHit <- TRUE
				break } }
		if( !fHit ) {
			break }
		fHit <- FALSE
		for( strTwo in colnames( frmeCov ) ) {
			if( length( grep( strTarget, strTwo ) ) ) {
				fHit <- TRUE
				break } }
		if( !fHit ) {
			break }
#if( !length( grep( "mp[tm]", strCom ) ) ) {
#	next }
#		astrCom <- c(astrCom, sub( "_vs_All_annodb", "_mbx", sub( "mock_", "",
#			sub( ".alignments", "", strCom ) ) ))

		aiAbd <- grep( c_strRE, astrPAbd )
		aiCov <- grep( c_strRE, astrPCov )
		if( max( adGSAbd[aiAbd] ) > 0 ) {
			dCur <- funcAcc( adGSAbd[aiAbd] / sum( adGSAbd[aiAbd] ), frmeAbd[aiAbd, strOne] )
		} else {
			dCur <- 0 }
		adRMSE <- c(adRMSE, dCur)
		pCur <- NA
		if( max( adGSCov[aiCov] ) > 0 ) {
			try( pCur <- prediction( frmeCov[aiCov, strTwo], adGSCov[aiCov] ) ) }
		if( is.na( pCur ) || ( class( pCur ) == "try-error" ) ) {
			next }
		print( c(strOne, strTwo) )
		print( pCur )
		lsPred <- c(lsPred, pCur) }
	return( list( names = astrTargets, rmse = adRMSE, pred = lsPred ) ) }

funcScatter <- function( lsData, astrNames, astrTargets ) {
	c_aChars	<- c(20, 4, 1:5)
	
	for( iTarget in 1:length( astrTargets ) ) {
		frmeAbd <- lsData$abd
		for( iCol in 2:ncol( frmeAbd ) ) {
			strCol <- colnames( frmeAbd )[iCol]
			if( length( grep( astrTargets[iTarget], strCol ) ) ) {
				strTarget <- strCol
				break } }
		astrPaths <- c()
		for( strPath in rownames( frmeAbd ) ) {
			if( length( grep( c_strRE, strPath ) ) ) {
				astrPaths <- c(strPath, astrPaths) } }
	
		strBase <- colnames( frmeAbd )[1]
		adGSAbd <- frmeAbd[astrPaths, strBase] / max( 1e-10, sum( frmeAbd[astrPaths, strBase] ) )
		adX <- frmeAbd[astrPaths, strTarget]
		ad <- c(adX, adGSAbd)
		if( iTarget == 1 ) {
			if( length( adX ) ) {
				dMin <- 0 # min( ad )
				dMax <- max( ad )
			} else {
				adGSAbd <- c()
				dMin <- 0
				dMax <- 0 }
			adLim <- c(0.99 * dMin, 1.01 * dMax)
			plot( adX, adGSAbd, xlim = adLim, ylim = adLim, xlab = "Predicted", ylab = "Actual",
				main = "Relative Abundance", pch = c_aChars[iTarget] )
		} else {
			points( adX, adGSAbd, pch = c_aChars[iTarget] ) }
		if( length( adX ) ) {
			lmod <- lm( adGSAbd ~ adX )
			abline( reg = lmod )
			dX <- 0.6 * dMax
			dY <- predict( lmod, data.frame( adX = dX ) )
			dR <- sprintf( "%0.4f", funcAcc( adX, adGSAbd ) )
			text( dX, dY, bquote( rho == .(dR) ), pos = 4, offset = 0.67 ) } }
	abline( 0, 1, lwd = 2 )
	legend( "bottomright", astrNames, bg = "white", pch = c_aChars[1:length( astrNames )] )
}
	
funcSAUC <- function( lsData, astrNames, astrTargets ) {

	for( i in 1:length( astrTargets ) ) {
		astrTargets[i] <- gsub( "-", ".", astrTargets[i] ) }
	funcScatter( lsData, astrNames, astrTargets )
	lsBase <- funcBase( lsData, astrTargets )
	funcPlotCov( lsBase$pred, astrNames )
}

c_iWidth	<- 5.5
c_iHeight	<- 4.5
c_dFPR		<- 0.1

c_astrTargets	<- c("mock_stg_hc_vs_All_annodb-htc-keg-mpm-cop-nul-nve-nul-nve", "mock_stg_hc_vs_All_annodb-htc-keg-nve-nul-nul-nul-nul")
strType			<- "mock_stg_hc"
c_strRE			<- '^M[0-9]+$' # '^ko[0-9]+$'
c_strOutput		<- paste( strType, ".pdf", sep = "" )
c_strCoverage	<- paste( "output/", strType, "_04a.txt", sep = "" )
c_strAbundance	<- paste( "output/", strType, "_04b.txt", sep = "" )
c_astrNames		<- c("HUMAnN", "best-BLAST-hit")

lsData <- funcData( c_strCoverage, c_strAbundance )
fPDF <- length( grep( "\\.pdf$", c_strOutput ) )
if( fPDF ) {
	pdf( c_strOutput, width = 2 * c_iWidth, height = c_iHeight )
} else {
	png( c_strOutput, units = "in", res = 160, width = 2 * c_iWidth, height = c_iHeight ) }
par( mfrow = c(1, 2) )
funcSAUC( lsData, c_astrNames, c_astrTargets )
dev.off( )
