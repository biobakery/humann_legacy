library( ROCR )

funcAcc <- function( adX, adY ) {

	if( is.null( adX ) || is.null( adY ) ) {
		return( 0 ) }
	return( cor( adX, adY ) ) }

funcClean <- function( frmeData, lsPathways = list() ) {
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
	
	if( length( lsPathways ) ) {
		aiRemove <- c()
		for( iRow in 1:nrow( frmeData ) ) {
			strRow <- rownames( frmeData )[iRow]
			if( ( strRow %in% names( lsPathways ) ) && ( length( lsPathways[[strRow]] ) < c_iSize ) ) {
				aiRemove <- c(aiRemove, iRow) } }
		frmeData <- frmeData[setdiff( 1:nrow( frmeData ), aiRemove ),] }
	
	return( frmeData ) }

funcData <- function( strCov, strAbd, lsPathways = list() ) {
	
	frmeCov <- read.delim( strCov, row.names = 1 )
	frmeAbd <- read.delim( strAbd, row.names = 1 )
	frmeCov <- funcClean( frmeCov, lsPathways )
	frmeAbd <- funcClean( frmeAbd, lsPathways )
	
	return( list( abd = frmeAbd, cov = frmeCov ) ) }

funcAUC <- function( pPred ) {

	if( is.na( pPred ) ) {
		return( 0 ) }
	pPerf <- performance( pPred, "auc", fpr.stop = c_dFPR )
	return( pPerf@y.values[1][[1]] / c_dFPR ) }

funcPlotTicklabels <- function( adX, astrCom, dMin ) {

	aiTargets <- c()
	for( i in 1:length( astrCom ) ) {
		if( length( grep( c_strTarget, astrCom[i] ) ) ) {
			aiTargets <- c(aiTargets, i) } }
	if( length( aiTargets ) ) {
		adCur <- adX[-aiTargets]
		astrCur <- astrCom[-aiTargets] }
	else {
		adCur <- adX
		astrCur <- astrCom }
	text( adCur, dMin * 0.999, astrCur, xpd = TRUE, srt = -45, adj = 0 )
	if( length( aiTargets ) ) {
		text( adX[aiTargets], dMin * 0.999, astrCom[aiTargets], xpd = TRUE, srt = -45, adj = 0, font = 2 ) } }

funcPlotAbd <- function( adRMSE, astrCom, strTitle ) {

	afRMSE <- adRMSE > 0
	adRMSE <- adRMSE[afRMSE]
	astrCom <- astrCom[afRMSE]
	if( !length( adRMSE ) ) {
		adRMSE <- c(0)
		astrCom <- c("") }

	par( mar = c(10, 4, 3, 2.75) + 0.1 )
	dMin <- min( adRMSE ) * 0.99
	adX <- barplot( adRMSE, ylim = c(dMin, max( adRMSE ) * 1.01), xpd = FALSE,
		ylab = "Correlation", main = sprintf( "%s Abundance", strTitle ) )
	funcPlotTicklabels( adX, astrCom, dMin ) }

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
		ylab = "pAUC", main = sprintf( "%s Coverage (pAUC %g)", strTitle, c_dFPR ) )
	funcPlotTicklabels( adX, astrCom, dMin ) }

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
		strName <- sub( ".nul.((nve)|(nul))(.xpe)?$", "", strName )
		strName <- sub( "nve.nve.nul.nul.nul$", " -All BBH", strName )
		strName <- sub( "^(.{3}\\..{7}).nae", "\\1 +GFAve", strName )
		strName <- sub( "^(.{3}\\..{7}).nve", "\\1 +GF", strName )
		strName <- sub( "^(.{3}\\..{7}).nul", "\\1 -GF", strName )
		strName <- sub( "^(.{3}\\..{3}).wbl", "\\1 +SmWB", strName )
		strName <- sub( "^(.{3}\\..{3}).nve", "\\1 +Sm", strName )
		strName <- sub( "^(.{3}\\..{3}).nul", "\\1 -Sm", strName )
		strName <- sub( "^(.{3})\\.cop", "\\1 +TaxC#", strName )
		strName <- sub( "^(.{3})\\.nve", "\\1 +Tax", strName )
		strName <- sub( "^(.{3})\\.nul", "\\1 -Tax", strName )
		strName <- sub( "^mpm", " Mod. +MP", strName )
		strName <- sub( "^nve", " Path -MP", strName )
		strName <- sub( "^mpt", " Path +MP", strName )
		strName <- gsub( "_", " ", strName )
#		print(strName)
		astrCom <- c(astrCom, strName)

		if( length( grep( "mtc", strCom ) ) ) {
			aiAbd <- setdiff( 1:length( astrPAbd ), grep( '^((ko)|M|K)[0-9]+$', astrPAbd ) )
			aiCov <- setdiff( 1:length( astrPCov ), grep( '^((ko)|M|K)[0-9]+$', astrPCov ) )
		} else if( length( grep( "keg\\.((mpt)|(nve))", strCom ) ) ) {
			print( strCom )
			aiAbd <- grep( "^((ko)|K)[0-9]+$", astrPAbd )
			aiCov <- grep( "^((ko)|K)[0-9]+$", astrPCov )
		} else {
			aiAbd <- grep( "^(M|K)[0-9]+$", astrPAbd )
			aiCov <- grep( "^(M|K)[0-9]+$", astrPCov ) }
		
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

funcFiles <- function( astrFiles ) {
	
	strPathways <- ""
	lsRet <- list()
	for( strFile in astrFiles ) {
		if( !length( grep( "\\.txt$", strFile  ) ) ) {
			if( nchar( strPathways ) ) {
				stop( "Multiple pathway files found: ", strPathways, strFile ) }
			strPathways <- strFile
			next }
		strType <- sub( ".*04([ab]).*", "\\1", strFile )
		iType <- ifelse( strType == "a", 1, 2 )
		strBase <- sub( "^(.*\\/)?(\\S+)_04[ab].*", "\\2", strFile )
		fHit <- FALSE
		if( length( lsRet ) ) {
			for( i in 1:length( lsRet ) ) {
				if( strBase == names( lsRet )[i] ) {
					fHit <- TRUE
					lsRet[[i]][iType] <- strFile
					break } } }
		if( !fHit ) {
			astrBase <- c()
			astrBase[iType] <- strFile
			lsRet[[strBase]] <- astrBase } }
	if( length( lsRet ) ) {
		for( i in 1:length( lsRet ) ) {
			iHits <- 0
			for( strCur in 1:length( lsRet[[i]] ) ) {
				if( !is.na( strCur ) ) {
					iHits <- 1 + iHits } }
			if( iHits != 2 ) {
				stop( "No file pair found for base: ", names( lsRet )[[i]] ) } } }
	return( list(lsFiles = lsRet, strPathways = strPathways) )
}

funcRun <- function( astrFiles, strOutput ) {
	
	lsTmp <- funcFiles( astrFiles )
	lsFiles <- lsTmp$lsFiles
	strPathways <- lsTmp$strPathways

	lsPathways <- list()
	if( nchar( strPathways ) ) {
		lsPathways <- funcPathways( strPathways ) }
	
	fPDF <- length( grep( "\\.pdf$", strOutput ) )
	for( i in 1:length( lsFiles ) ) {
		astrCur <- lsFiles[[i]]
		lsCur <- funcData( astrCur[1], astrCur[2], lsPathways )
		strBase <- names( lsFiles )[i]
		strTitle <- ""
		if( length( grep( "even", strBase ) ) ) {
			strTitle <- sprintf( "%s %s", strTitle, "Even" ) }
		if( length( grep( "stg", strBase ) ) ) {
			strTitle <- sprintf( "%s %s", strTitle, "Stg." ) }
		if( length( grep( "hc", strBase ) ) ) {
			strTitle <- sprintf( "%s %s", strTitle, "HC" ) }
		if( length( grep( "lc", strBase ) ) ) {
			strTitle <- sprintf( "%s %s", strTitle, "LC" ) }
		
		if( i == 1 ) {
			iTypes <- min( 5000, max( ncol( lsCur$abd ), ncol( lsCur$cov ) ) - 1 )
			if( !is.finite( iTypes ) ) {
				iTypes <- 0 }
			iWidth <- 1 + ( iTypes / 30 )
			if( fPDF ) {
				pdf( strOutput, width = 2 * iWidth * c_iWidth, height = c_iHeight * length( lsFiles ) )
			} else {
				png( strOutput, units = "in", res = 160, width = 2 * iWidth * c_iWidth, height = c_iHeight * length( lsFiles ) ) }
			par( mfrow = c(length( lsFiles ), 2) ) }

		lsBase <- funcBase( lsCur )
		funcPlotAbd( lsBase$rmse, lsBase$names, strTitle )
		funcPlotCovAUC( lsBase$pred, lsBase$names, strTitle ) }
	if( dev.cur( ) != 1 ) {
		dev.off( ) } }

funcPathways <- function( strFile ) {
	
	lsRet <- list()
	for( strLine in readLines( strFile ) ) {
		astrLine <- strsplit( strLine, "\t" )[[1]]
		lsRet[astrLine[1]] <- list(astrLine[2:length( astrLine )]) }
	
	return( lsRet ) }

c_iWidth		<- 4
c_iHeight		<- 3
c_dFPR			<- 0.1
c_iSize			<- 6
c_strTarget		<- " \\+MP \\+TaxC# -Sm \\+GF$"

strOutput		<- "output/mocks.pdf"
astrFiles		<- c("output/mock_stg_hc_04a.txt", "output/mock_stg_hc_04b.txt")
astrArgs <- commandArgs( TRUE )
if( length( astrArgs ) >= 1 ) {
	strOutput <- astrArgs[1] }
if( length( astrArgs ) >= 2 ) {
	astrFiles <- astrArgs[2:length( astrArgs )] }

funcRun( astrFiles, strOutput )
