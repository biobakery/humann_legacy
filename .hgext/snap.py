# snap.py version (big) file snapshots with storage outside hg repo
#
# Copyright 2010 Klaus Koch <kuk42@gmx.net>
#
#
# The basic approach is to add snap:1 to filelog meta for files bigger
# than a given threshold or matching given patterns.  The content of
# such files is then stored in more or less compressed files in a
# separate directory.  The data stored in the repository consists of a
# single string '.snap://<filename>.<sha1>\n' which acts as a pointer
# to the original data.
#
# Currently, each file snapshot is stored in its own zip file.  This
# could be improved by accumulating several snapshots of the same file
# in the same zip file up to a certain size.  However, that would make
# other things more complicated like finding a snapshot, and in
# particular pushing and pulling it, finally requiring a wire protocol
# for snap stores.  Indeed, instead of zip files revlogs could be
# used, only if revlog stored snapshots bigger than 4 GiB, and those
# could be transmitted by the normal wire protocol (preferable
# together with some shallow clone feature).
#
# Sha1 collisions may be very unlikely, but they are not impossible.
# So, if a snapshot is stored with the same sha1 as another file in
# the snap store, the data of the two snapshots is checked to ensure
# that no hash collision occurred.  If the data differs, an integer
# suffix '_%d' is added to the hash of the new snapshot.
#
# In case a file snapshot is requested which has been removed, e.g. to
# save space, an error message is printed.  This could be avoided by
# keeping a 'manifest' file with all files which have been removed on
# purpose.  Not implemented so far, because missing files break
# Mercurial's consistency guarantees and thus should always be
# reported.
#
# Filters are ignored for snapped files' data, because the data is
# read iteratively with arbitrary block sizes.  Most filters assume
# that they get the entire data in one chunk, e.g. win32text's
# cleverencode first searches for '\0' in the data to determine
# whether a file is binary, before the data is translated.  Since more
# than one filter may be applied, we cannot know what character
# combination must not be broken for a particular filter (without
# extending the filter configuration and methods).
#
# For source repos without pushkey capability, cloning takes at least
# three times longer, if the source's snap store contains files.  We
# maintain a map file in .hg/snap/filemap and make it listable in
# pushkey namespace snapfilemap.  It contains the names of reverenced
# snap files per revision newly reverencing them.
#
# Nested Mercurial queue patch dir repos are not snappy, but the
# enclosing repo is.
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""version (big) file snapshots with storage outside a Mercurial repo

Some files are either too big, or do not change in small enough deltas
to be stored in a source revision system like Mercurial.  They
increase the repository size, memory consumption, and run-time.

Such files show a _current_ size bigger than a threshold (default:
999999 bytes), or match a configured pattern, but are no symlinks or
have names starting with `.hg`.

With this extension, the huge data of such files is never seen by a
Mercurial repository.  Instead, their content is saved outside the
repository, and Mercurial gets an additional filelog meta `snap:1` and
a string `.snap://<data_store_filename>.<sha1>\n` as file data, where
the sha1 is computed out of the original data during commit.  The file
is `snapped`.

One can use Mercurial's commands as usual, e.g. :hg:`log <snapped
file>`, :hg:`merge` etc.  For the latter, snapped files are always
merged with `internal:fail`, i.e., they are never automatically
merged, excepting the environment variable HGMERGE is set to one of
`internal:(local, other, dump)`, or they are merged by a tool in
`merge-tools` with the new attribute `snap` set (see :hg:`help config`
for details on merge-tools).  One can resolve such failed merges as
usual with :hg:`resolve.

Note: The filelog meta `snap:1` is not kept by the convert extension
delivered with Mercurial, however, this extension adapts it, if
activated.  Due to the stored string it is always possible to repair a
repository which has been converted without this extension (see
options in :hg:`help convert`).

Note: This extension is ineffective regarding Mercurial extensions
using their own methods for opening files in the working directory.
It may help to set the `pre-<cmd>` and `post-<cmd>` hooks of the
extensions commands to `python:snap.snapcache`, and
`python:snap.snapupdate` (or the hook snap.snapudate you set up, see
below), respectively (see :hg:`help config` for details on hooks).

Note: Filters for transforming snapped files on checkout/checkin must
be set up as update/precommit hooks, because Mercurial's
`decode/encode` mechanism reads the entire file data into memory,
whereas this extension reads the data iteratively in blocks.  Since
snap cannot know what character combinations must be kept together for
filters to work, it ensures the filters see only the snap string.
Consequently, such filters should reconstruct the snap string, or keep
it intact.  Mercurial's `decode/encode` filters are applied to the
snap string, not to the snapped data content.

Note: External patch programs will directly process the (big) files in
the working dir.  External diff and merge programs, if called by the
``extdiff`` extension, will only see the snap strings.

Files which Mercurial suspects modified (changed modification time,
but not size or mode) trigger a re-computation of their snap string
and hash to check if they really changed.  This could happen e.g. with
:hg:`status` and may take some time, see config snap.slack_factor
below for accelerating this.

When a snapped file is commited, its original data is stored together
with some metadata into a read-only zip file named like the original
file in Mercurial's data store with the sha1 attached, and put into
the snap store path `snap-store` (default: .hg/snap/cache).  The file
in the working dir is not touched in any way.  The compression level
can be configured as well as the file suffixes for files to be stored
directly.  The zip files can be regenerated later with better
compression.  One can search their content with :hg:`cat -r <rev>
<file name>`.

When a changeset with snapped files is pulled, the snapped files are
hardlinked or copied from the remote's snapstore or `snap-default`
into the locals' snapstore or into `snap-store`, just before the hook
`changegroup` is called.
If a changeset is pushed, its snapped files are hardlinked or copied
from the local's snapstore or `snap-store` to the remote's snapstore
or `snap-default-push` or `snap-default`.
Alternatively, one could synchronize snap stores directly with
:hg:`debugsnappull` or :hg:`debugsnappush`.
Whenever any path of `snap-store`, `snap-default` or
`snap-default-push` is defined, it is used instead of a local or
(default) remote repo's local store.

In case a repository with snapped files in its snap store is cloned,
the referenced snap files are pulled after the clone has been created.

Recipients of Mercurial bundles or patches need access to a snap
store, or referenced snapped files must be provided separately.  This
could be done with :hg:`debugsnappull` or :hg:`debugsnappush`.
Patches with snap strings can be applied only to files in working dir
which are either not yet snapped or contain the to be replaced snap
string.  That is, already snapped files which are to be patched, must
be first reverted with :hg:`revert --nosnapped` so that the snap
string is the content of the working dir file.

When a snapped file is updated, shelved or unshelved, its snap string
is first written into the file in the working directory, then the hook
`snapupdate` (default: python:snap.snapupdate) is executed just before
the hook `update`.

If the hook `snapupdate` can not retrieve a file, this is reported and
the file's clean working dir version containing its snap string is
deleted.  Hence, snapped files can be removed from the snap store to
save disk space, and programs will never see files with their content
replaced by snap strings.

Following settings can be configured (the defaults are shown)::

    [paths]
    snap-store = <repo path>.hg/snap/cache
    snap-default =
    snap-default-push =

    [snap]
    size_threshold = 999999 # (bytes, i.e., ca. 9.5 MiB; must be < 715 MiB)
    slack_factor = -1       # always compute valid temporary hash
    patterns =

    compresslevel = 9  # 0 to 9 (none to best compression)
    avoid_compression_suffixes = .gz .bz2 .zip .Z .rar .ta2 .tgz .taz .tlz .tlz .zoo .arc .lzh .arj .lzma .xz

    [hooks]     # called before the hook of same name without prefix `snap`
    snapupdate = python:snap.snapupdate  ## if deactivated, use snap.snapdelete

`snap.patterns`
 A comma/space separated list of patterns as described by :hg:`help patterns`.
`snap.avoid_compression_suffixes`
 A comma/space separated list defining file extensions of file types
 not to be compressed.
`snap.slack_factor`
 Mercurial checks the content of files which changed in modification
 time, but not in size or mode.  If slack_factor is unequal -1 and a
 file's size is bigger than size_threshold times slack_factor,
 Mercurial just gets an internal snap string with temporary hash
 `-1-1-1-1-1-1-1-1-1-1-1-1`.  This saves time, e.g. for :hg:`status`.
 A side effect is that :hg:`remove` refuses to delete the file,
 because it seems modified (use -f to remove anyway).  When its real
 sha1 is resolved during commit, it might turn out that only the
 modification time changed and so nothing is commited.  You may
 consider it as checked out in the sense of centralized source
 revision systems.

See documentation of `ssymlink` for further details and requirements
for hook snapupdate.  One can config it to only update not snapped files.

The commands `status`, `cat`, `diff`, `revert`, `archive`, `verify`,
`serve`, and `convert` got new options (some convert features require
a central snap store, i.e., snap-store and snap-default).
"""
import os, cStringIO, sys, tempfile, struct, time, errno, zipfile, zlib, shutil, warnings, socket, calendar
from os import stat_result
from math import ceil as _ceil

try:
    from mercurial.i18n import _
except ImportError, e:
    e.args += ('set PYTHONPATH to Mercurial Python libs',)
    raise

from mercurial import (localrepo, extensions, commands, util, cmdutil,
                       dispatch, hg, url, archival, dirstate, context,
                       repair, ui, filemerge, merge, error, filelog, revlog,
                       encoding, parsers, sshrepo, httprepo, sshserver,
                       httpserver, store, patch, mdiff, discovery)
from mercurial import match as _match
from mercurial.url import hidepassword as _hidepassword
from mercurial.node import hex as _hex, bin as _bin, nullrev, nullid
from mercurial.store import _auxencode, _hybridencode # 
from mercurial.context import changectx, filectx, memctx, memfilectx

# Check again in wrap_convert for correct paths/modules.
import hgext.convert
import hgext.convert.hg

try:
    from mercurial import templatekw

    def showfilesnapped(**args):
        repo = args['repo']
        ctx = args['ctx']
        node = ctx.node()
        man = ctx.manifest()
        s = ['%s (%40s)' % (f, snappedname(repo, ctx[f]))
             for f in ctx if f in man and ctx[f].issnap()]
        return templatekw.showlist('files_snapped', s, plural='files_snapped',
                                   **args)
    templatekw.keywords.setdefault('files_snapped', showfilesnapped)
except ImportError:
    raise util.Abort(_('snap extension requires Mercurial version >= 1.6'))


_sha1 = util.sha1
avoid_compression_suffixes = ['.gz', '.bz2', '.zip', '.Z', '.rar',
                              '.ta2' , '.tgz', '.taz', '.tlz', '.tlz',
                              '.zoo', '.arc', '.lzh', '.arj', '.lzma', '.xz']



def snappedname(repo, fctx=None, plain=True):
    """return snapped storage file name of file context's data"""
    try:
        s = repo.wwritedata(fctx.path(), fctx.data())
    except AttributeError:
        s = fctx
    if not s.startswith(snapprefix):
        raise util.Abort(_('%r ... is no snapped file string') % s[:163])
    s = util.drop_scheme(snapscheme, s.rstrip('\n\r'))
    util.path_auditor(repo.root)(s)
    if plain:
        return s
    else:
        return hybridencode(s)

def auxencode(f):
    return _auxencode(f, True)

def hybridencode(path):
    """stored snap file names get the same handling as Mercurial data files"""
    hpath = _hybridencode('data/'+path, auxencode)
    if hpath.startswith('dh/'):
        return hpath[len('dh/'):]
    elif hpath.startswith('data/'):
        return hpath[len('data/'):]
    raise util.Abort(
        _("this Mercurial's hybridencode returns unexpected path encoding"))


def _threshold(ui):
    hard_size_threshold = 750000000 # ~ current actual limit for 32bit systems
    size_threshold = int(ui.config('snap', 'size_threshold', default=9999999))
    if size_threshold > hard_size_threshold:
        ui.warn(_("setting snap.size_threshold=%r is beyond current hard"
                  " max file size limit %r, will use that instead\n" %
                  (size_threshold, hard_size_threshold)))
        size_threshold = hard_size_threshold
    return size_threshold


def _snapmatch(ui, root, cwd=None):
    cwd = cwd or ''
    if not os.path.isabs(cwd):
        snappats = ui.configlist('snap', 'patterns', None)
        if snappats:
            return _match.match(root, cwd, [], include=snappats)
    return lambda m: False


def _dirlike(url):
    """return True, if cachepath must not be joined to url"""
    return url[:url.find(':')] in ('ssh', 'file')

cachepath = 'snap/cache'
defaultsnappaths = ('snap-store', 'snap-default', 'snap-default-push')
def _repojoin(repo, path):
    if repo.url().startswith('bundle:'):
        raise error.RepoError(_('no store at %s') % repo.url())
    try:
        path = repo.join(path)
    except AttributeError:
        url = repo.url()
        if not _dirlike(url):
            return url
        if url.endswith('/'):
            url = url[:-1]
        path = url + '/.hg/' + util.pconvert(path)
    return path


# some options are not propagated to hooks (--ssh, --remotecmd),
# _parseopts gets them
try:                        # TortoiseHG uses its own option parser(s)
    import tortoisehg
    try:
        import tortoisehg.hgtk.hgtk as hgtk_hgtk
        def _parseopts(ui, args):
            try:
                return hgtk_hgtk._parse(ui, args)[-2] # 
            except ImportError:
                return dispatch._parse(ui, args)[-1] # 
    except ImportError:
        import tortoisehg.hgqt.run as hgqt_run
        def _parseopts(ui, args):
            try:
                return hgqt_run._parse(ui, args)[-2] # 
            except ImportError:
                return dispatch._parse(ui, args)[-1] # 
except ImportError:
    def _parseopts(ui, args):
        return dispatch._parse(ui, args)[-1] # 

def _store(ui, repo=None, path=None, create=0, repo2=None):
    path = util.localpath(hg.localpath(ui.expandpath(path or 'snap-store')))
    # some options are not propagated to hooks (--ssh, --remotecmd)
    opts = dict(_parseopts(ui, sys.argv[1:]))
    remoteui = hg.remoteui(ui, opts)
    if path in defaultsnappaths and repo:
        if isinstance(repo, str):
            repo = hg.repository(remoteui, repo)
        try:
            path = os.path.join(repo.sharedpath, cachepath)
        except AttributeError:  # no shared repository
            path = _repojoin(repo, cachepath)
    try:
        return _lookup(path)(remoteui, path, create=create)
    except error.RepoError:
        if not repo2:
            raise
        # check out other 'repo2' (useful for pull from bundle)
        return _store(ui, repo=repo2)


def _compresslevel(ui, fname):
    """determine compress level for file name"""
    n, ext = os.path.splitext(fname)
    if ext in ui.configlist('snap', 'avoid_compression_suffixes',
                            default=avoid_compression_suffixes):
        return 0
    return int(ui.config('snap', 'compresslevel', default=6))


def ret_progress(ui, topic, unit='kiB', total=None):
    def f(i):
        return ui.progress(topic, i, unit=unit, total=total)
    return f

def noprogress(*args, **kwargs):
    pass

def _kiB(i):
    return int(_ceil(i/1024.))

_length = 16 * 1024
def _copyfileobj(fsrc, fdst, progress=None):
    """copy data from file object fsrc to file-like object fdst, return sha1, size"""
    progress = progress or noprogress
    s = _sha1('')
    i = 0
    while 1:
        if True:
            buf = fsrc.read(_length)
            if not buf:
                break
            i += len(buf)
            progress(int(i/1024))
            s.update(buf)
            fdst.write(buf)

    progress(None)
    return s.hexdigest(), i


class FilesDiffer(Exception):
    pass


def _copyfileobjcmp(fsrc, fdst, fref, progress=None):
    """copy data from file object fsrc to file-like object fdst, return (sha1, size), raise FilesDiffer exception if files differ
    """
    progress = progress or noprogress
    s = _sha1('')
    i = 0
    while 1:
        if True:
            buf = fsrc.read(_length)
            rbuf = fref.read(_length)
            if (buf != rbuf):
                raise FilesDiffer
            if not buf:
                break
            i += len(buf)
            progress(int(i/1024))
            s.update(buf)
            fdst.write(buf)

    return s.hexdigest(), i



if not getattr(zipfile.ZipFile, 'open', None): # Python < 2.6
    class _ZipExtFile:
        """File-like object for reading an archive member.
           Is returned by ZipFile.open().
        """

        def __init__(self, fileobj, zipinfo, decrypt=None):
            self.fileobj = fileobj
            self.decrypter = decrypt
            self.bytes_read = 0L
            self.rawbuffer = ''
            self.readbuffer = ''
            self.linebuffer = ''
            self.eof = False
            self.univ_newlines = False
            self.nlSeps = ("\n", )
            self.lastdiscard = ''

            self.compress_type = zipinfo.compress_type
            self.compress_size = zipinfo.compress_size

            self.closed  = False
            self.mode    = "r"
            self.name = zipinfo.filename

            # read from compressed files in 64k blocks
            self.compreadsize = 64*1024
            if self.compress_type == zipfile.ZIP_DEFLATED:
                self.dc = zlib.decompressobj(-15)

        def set_univ_newlines(self, univ_newlines):
            self.univ_newlines = univ_newlines

            # pick line separator char(s) based on universal newlines flag
            self.nlSeps = ("\n", )
            if self.univ_newlines:
                self.nlSeps = ("\r\n", "\r", "\n")

        def __iter__(self):
            return self

        def next(self):
            nextline = self.readline()
            if not nextline:
                raise StopIteration()

            return nextline

        def close(self):
            self.closed = True

        def _checkfornewline(self):
            nl, nllen = -1, -1
            if self.linebuffer:
                # ugly check for cases where half of an \r\n pair was
                # read on the last pass, and the \r was discarded.  In this
                # case we just throw away the \n at the start of the buffer.
                if (self.lastdiscard, self.linebuffer[0]) == ('\r','\n'):
                    self.linebuffer = self.linebuffer[1:]

                for sep in self.nlSeps:
                    nl = self.linebuffer.find(sep)
                    if nl >= 0:
                        nllen = len(sep)
                        return nl, nllen

            return nl, nllen

        def readline(self, size=-1):
            """Read a line with approx. size. If size is negative,
               read a whole line.
            """
            if size < 0:
                size = sys.maxint
            elif size == 0:
                return ''

            # check for a newline already in buffer
            nl, nllen = self._checkfornewline()

            if nl >= 0:
                # the next line was already in the buffer
                nl = min(nl, size)
            else:
                # no line break in buffer - try to read more
                size -= len(self.linebuffer)
                while nl < 0 and size > 0:
                    buf = self.read(min(size, 100))
                    if not buf:
                        break
                    self.linebuffer += buf
                    size -= len(buf)

                    # check for a newline in buffer
                    nl, nllen = self._checkfornewline()

                # we either ran out of bytes in the file, or
                # met the specified size limit without finding a newline,
                # so return current buffer
                if nl < 0:
                    s = self.linebuffer
                    self.linebuffer = ''
                    return s

            buf = self.linebuffer[:nl]
            self.lastdiscard = self.linebuffer[nl:nl + nllen]
            self.linebuffer = self.linebuffer[nl + nllen:]

            # line is always returned with \n as newline char (except possibly
            # for a final incomplete line in the file, which is handled above).
            return buf + "\n"

        def readlines(self, sizehint=-1):
            """Return a list with all (following) lines. The sizehint parameter
            is ignored in this implementation.
            """
            result = []
            while True:
                line = self.readline()
                if not line: break
                result.append(line)
            return result

        def read(self, size=None):
            # act like file() obj and return empty string if size is 0
            if size == 0:
                return ''

            # determine read size
            bytesToRead = self.compress_size - self.bytes_read

            # adjust read size for encrypted files since the first 12 bytes
            # are for the encryption/password information
            if self.decrypter is not None:
                bytesToRead -= 12

            if size is not None and size >= 0:
                if self.compress_type == zipfile.ZIP_STORED:
                    lr = len(self.readbuffer)
                    bytesToRead = min(bytesToRead, size - lr)
                elif self.compress_type == zipfile.ZIP_DEFLATED:
                    if len(self.readbuffer) > size:
                        # the user has requested fewer bytes than we've already
                        # pulled through the decompressor; don't read any more
                        bytesToRead = 0
                    else:
                        # user will use up the buffer, so read some more
                        lr = len(self.rawbuffer)
                        bytesToRead = min(bytesToRead, self.compreadsize - lr)

            # avoid reading past end of file contents
            if bytesToRead + self.bytes_read > self.compress_size:
                bytesToRead = self.compress_size - self.bytes_read

            # try to read from file (if necessary)
            if bytesToRead > 0:
                bytes = self.fileobj.read(bytesToRead)
                self.bytes_read += len(bytes)
                self.rawbuffer += bytes

                # handle contents of raw buffer
                if self.rawbuffer:
                    newdata = self.rawbuffer
                    self.rawbuffer = ''

                    # decrypt new data if we were given an object to handle that
                    if newdata and self.decrypter is not None:
                        newdata = ''.join(map(self.decrypter, newdata))

                    # decompress newly read data if necessary
                    if newdata and self.compress_type == zipfile.ZIP_DEFLATED:
                        newdata = self.dc.decompress(newdata)
                        self.rawbuffer = self.dc.unconsumed_tail
                        if self.eof and len(self.rawbuffer) == 0:
                            # we're out of raw bytes (both from the file and
                            # the local buffer); flush just to make sure the
                            # decompressor is done
                            newdata += self.dc.flush()
                            # prevent decompressor from being used again
                            self.dc = None

                    self.readbuffer += newdata


            # return what the user asked for
            if size is None or len(self.readbuffer) <= size:
                bytes = self.readbuffer
                self.readbuffer = ''
            else:
                bytes = self.readbuffer[:size]
                self.readbuffer = self.readbuffer[size:]

            return bytes

        def _ZipFileopen(self, name, mode="r", pwd=None):
            """Return file-like object for 'name'."""
            if mode not in ("r", "U", "rU"):
                raise RuntimeError, 'open() requires mode "r", "U", or "rU"'
            if not self.fp:
                raise RuntimeError, \
                      "Attempt to read ZIP archive that was already closed"

            # Only open a new file for instances where we were not
            # given a file object in the constructor
            if self._filePassed:
                zef_file = self.fp
            else:
                zef_file = open(self.filename, 'rb')

            # Make sure we have an info object
            if isinstance(name, zipfile.ZipInfo):
                # 'name' is already an info object
                zinfo = name
            else:
                # Get info object for name
                zinfo = self.getinfo(name)

            zef_file.seek(zinfo.header_offset, 0)

            # Skip the file header:
            sizeFileHeader = struct.calcsize(zipfile.structFileHeader)
            fheader = zef_file.read(sizeFileHeader)
            if fheader[0:4] != zipfile.stringFileHeader:
                raise BadZipfile, "Bad magic number for file header"

            fheader = struct.unpack(zipfile.structFileHeader, fheader)
            fname = zef_file.read(fheader[zipfile._FH_FILENAME_LENGTH])
            if fheader[zipfile._FH_EXTRA_FIELD_LENGTH]:
                zef_file.read(fheader[zipfile._FH_EXTRA_FIELD_LENGTH])

            if fname != zinfo.orig_filename:
                raise zipfile.BadZipfile, \
                          'File name in directory "%s" and header "%s" differ.' % (
                              zinfo.orig_filename, fname)

            # check for encrypted flag & handle password
            is_encrypted = zinfo.flag_bits & 0x1
            zd = None
            if is_encrypted:
                if not pwd:
                    pwd = self.pwd
                if not pwd:
                    raise RuntimeError, "File %s is encrypted, " \
                          "password required for extraction" % name

                zd = _ZipDecrypter(pwd)
                # The first 12 bytes in the cypher stream is an encryption header
                #  used to strengthen the algorithm. The first 11 bytes are
                #  completely random, while the 12th contains the MSB of the CRC,
                #  or the MSB of the file time depending on the header type
                #  and is used to check the correctness of the password.
                bytes = zef_file.read(12)
                h = map(zd, bytes[0:12])
                if zinfo.flag_bits & 0x8:
                    # compare against the file type from extended local headers
                    check_byte = (zinfo._raw_time >> 8) & 0xff
                else:
                    # compare against the CRC otherwise
                    check_byte = (zinfo.CRC >> 24) & 0xff
                if ord(h[11]) != check_byte:
                    raise RuntimeError("Bad password for file", name)

            # build and return a ZipExtFile
            if zd is None:
                zef = _ZipExtFile(zef_file, zinfo)
            else:
                zef = _ZipExtFile(zef_file, zinfo, zd)

            # set universal newlines on ZipExtFile if necessary
            if "U" in mode:
                zef.set_univ_newlines(True)
            return zef
        zipfile.ZipFile.open = _ZipFileopen



class snapZipFile(zipfile.ZipFile):
    def __init__(self, f, mode="rb"):
        zipfile.ZipFile.__init__(self, f, mode,
                                 compression=zipfile.ZIP_DEFLATED,
                                 allowZip64=True)
        self.objs_open = 0
        self.objzinfo = None

    def objopen(self, name, st_mode, st_mtime, compresslevel):
        """write file obj into """
        if not self.fp:
            raise RuntimeError(
                  "Attempt to write to ZIP archive that was already closed")
        if self.objs_open:
            raise RuntimeError("Attempt to write to ZIP archive by two objects")
        self.objs_open += 1     # 
        zinfo = zipfile.ZipInfo(name, time.localtime(st_mtime)[0:6])
        dt = zinfo.date_time
        if ((dt[0] - 1980) << 9 | dt[1] << 5 | dt[2]) < 0:
            zinfo = zipfile.ZipInfo(name) # use 1980/1/1, file is older than DOS
        zinfo.external_attr = (st_mode & 0xFFFF) << 16L      # Unix attributes
        zinfo.compress_type = self.compression
        if compresslevel == 0:
            zinfo.compress_type = zipfile.ZIP_STORED
        if zinfo.compress_type == zipfile.ZIP_DEFLATED:
            self.objcmpr = zlib.compressobj(compresslevel, zlib.DEFLATED, -15)
        zinfo.flag_bits = 0x00
        zinfo.header_offset = self.fp.tell()    # Start of header bytes
        zinfo.file_size = 0
        self._writecheck(zinfo)
        self._didModify = True
        # Must overwrite CRC and sizes with correct data later
        zinfo.CRC = 0
        zinfo.compress_size = 0
        self.fp.write(zinfo.FileHeader())
        self.objzinfo = zinfo

    def objwrite(self, buf):
        zinfo = self.objzinfo
        zinfo.file_size += len(buf)
        zinfo.CRC = zlib.crc32(buf, zinfo.CRC) & 0xffffffff
        if zinfo.compress_type != zipfile.ZIP_STORED:
            buf = self.objcmpr.compress(buf)
        zinfo.compress_size += len(buf)
        self.fp.write(buf)

    def objclose(self):
        if self.objs_open:
            zinfo = self.objzinfo
            buf = ''
            if zinfo.compress_type != zipfile.ZIP_STORED:
                buf = self.objcmpr.flush()
            self.fp.write(buf)
            zinfo.compress_size += len(buf)
            # Seek backwards and write CRC and file sizes
            position = self.fp.tell()       # Preserve current position in file
            self.fp.seek(zinfo.header_offset + 14, 0)
            compress_size = zinfo.compress_size
            if compress_size > 2**32 - 1:
                compress_size -= 2**32 - 1
            file_size = zinfo.file_size
            if file_size > 2**32 - 1:
                file_size -= 2**32 - 1
            self.fp.write(struct.pack("<LLL", zinfo.CRC, compress_size,
                                      file_size))
            self.fp.seek(position, 0)
            self.filelist.append(zinfo)
            self.NameToInfo[zinfo.filename] = zinfo
            self.objs_open -= 1



class snapStoreFile(object):
    def __init__(self, dest, mode, compresslevel=6, sha1=None, **meta):
        self._metaname = '.hg/snap/metadata'
        self.zip = snapZipFile(dest, mode)
        if ('w' in mode):
            self.zip.objopen(meta['name'], meta['lstat'].st_mode,
                             meta['lstat'].st_mtime, compresslevel)
        else:
            name = self.meta()['name'][:-1]
            self.s = self.zip.open(name, 'r')

    def write(self, s):
        self.zip.objwrite(s)

    def read(self, size=None):
        return self.s.read(size)

    def seek(self, offset, whence=0):
        if offset == 0 and whence == 0:
            self.s.close()
            self.s = self.zip.open(self.meta()['name'][:-1], 'r')
            return
        raise AttributeError

    def close(self):
        if getattr(self, 'zip', None):
            self.zip.objclose()
            self.zip.close()

    def __del__(self):
        self.close()

    def _setmeta(self, name=None, hname=None, lstat=None, metadata=None,
                 compresslevel=None, sha1=None):
        try:
            self.zip.objclose()
        except:
            pass
        s = ''.join(('name=%s\n' % name,
                     'hname=%s\n' % hname,
                     'sha1=%s\n' % sha1,
                     ('mtime=%s\nmode=%s\nsize=%s\n' % (int(lstat.st_mtime),
                                                        lstat.st_mode,
                                                        lstat.st_size)),
                     metadata,
                     'compresslevel=%s\n' % compresslevel))
        self.zip.writestr(self._metaname, s)

    def meta(self):
        """return dict with mtime=<int_str>, mode=<int_str>, size=<long_str>,
        compresslevel=<int_str>, and metadata as produced by :hg:`archive` like
        repo=<hex_str>, node=<hex_str>, ...)
        """
        name = getattr(self.zip, 'name', None) or \
            getattr(self.zip, 'filename', None)
        meta = self.zip.open(self._metaname, mode='r')
        try:
            d = dict(l.replace(': ', '=').split('=', 1) for l in meta)
        except:
            raise util.Abort(_('metadata %s in file %s is corrupted') % name)
        finally:
            meta.close()

        if None in d.values():
            raise util.Abort(_('invalid metadata value None for snapped'
                               ' file %s in %s: %r') % (self.name, name, d))
        required = ('mtime', 'mode', 'size', 'repo', 'node')
        missing = set(required).difference(d.keys())
        if missing:
            raise util.Abort(_("no %r in file's %s metadata %r") %
                             (missing, name, d))
        for k in required[:-2]:
            d[k] = long(d[k])
        return d



def snapsha(ui, repo, *pats, **opts):
    """print sha1 of files in working directory"""
    m = cmdutil.match(repo, pats, opts)
    devnull = open(os.devnull, 'wb')
    try:
        for f in repo[None].walk(m):
            size = int(os.lstat(m.rel(f)).st_size)
            fobj = open(m.rel(f), 'rb')
            try:
                h, s = _copyfileobj(fobj, devnull,
                                    ret_progress(ui, f, total=_kiB(size)))
                if size != s:
                    raise util.Abort(
                        _('%s: file size changed during hash computing?') % f)
                ui.status(_('%s %s\n' % (f, h)))
            finally:
                fobj.close()
    finally:
        devnull.close()


def debugsnapdata(ui, *files, **opts):
    """print metadata of files stored by snap extension"""
    fs = opts.get('field_separator').decode('string_escape')
    rs = opts.get('record_separator', '\n').decode('string_escape')
    recordtemp = '%s' + fs + '%s' + rs
    for f in files:
        try:
            g = snapStoreFile(f, 'r')
        except zipfile.BadZipfile, e:
            raise util.Abort(_('%s: no snapped file: %s') % (f, e))
        try:
            ui.write(recordtemp % (f,
                                   fs.join(fs.join((k, str(v).rstrip('\n')))
                                           for k, v in g.meta().items())))
        finally:
            g.close()


def _resolveshacollision(ui, dest, cdest, dest_h, src, srclstat):
    """return a new or old cdest for which no sha collision occurs"""
    ui.note('%s' % dest)
    odest = dest
    i = 0
    while 1:
        if (not os.path.lexists(cdest) or
            _checkshacollision(ui,
                               cdest, dest_h, src, srclstat) != _SHA_COLLISION):
            return cdest
        i += 1
        cdest = '%s_%s.zip' % (dest, i)

def _close(filehandle):
    if filehandle and not filehandle in (sys.stdout, sys.stderr):
        try:
            return filehandle.close()
        except AttributeError:
            del(filehandle)

def _checkshacollision(ui, cdest, dest_h, src, srclstat):
    """
    cdest : Name of file to be checked.
    dest_h : Expected hash of cdest
    src : File name which clashes with name cdest
    srclstat : The lstat of src

    In case cdest's original mtime and size (as set in the metadata)
    do not differ with src's, no collision is assumed.
    """
    fsrc = None
    fdst = None
    frep = None
    try:
        fsrc = snapStoreFile(cdest, mode='r')
        fsrcmeta = fsrc.meta()
        if (srclstat.st_size != int(fsrcmeta.get('size')) or
            int(srclstat.st_mtime) != int(fsrcmeta.get('mtime')) or
            dest_h != fsrcmeta.get('sha1')):
            fdst = open(os.devnull, 'wb')
            if getattr(src, 'read', None):
                fref = src
                fref.seek(0)
            else:
                fref = open(src, 'rb')
            try:
                size = int(srclstat.st_size)
                h, s = _copyfileobjcmp(fsrc=fsrc, fdst=fdst, fref=fref,
                                       progress=ret_progress(ui, 'check '+cdest,
                                                             total=_kiB(size)))
            except FilesDiffer:
                ui.note(_(', sha1 collision, try again\n'))
                return _SHA_COLLISION
            eh = dest_h.rsplit('_', 1)[0]
            if h != eh:
                raise util.Abort(_(", hash of already put %r is not %r,"
                                   " but %r\n" % (cdest, eh, h)))
            if size != s:
                raise util.Abort(_(", transferred bytes %s unequal"
                                   " file size %s") % (s, size))
        ui.note(_(', skip it\n'))
        return 0
    finally:
        _close(fsrc)
        _close(fdst)
        _close(frep)



def _metadata(repo, node, ctx):
    """stolen from mercurial.archival.archiver.metadata
    """
    ctx = ctx
    base = 'repo: %s\nnode: %s\nbranch: %s\n' % (
        _hex(repo.changelog.node(0)), _hex(node), ctx.branch())

    tags = ''.join('tag: %s\n' % t for t in ctx.tags()
                   if repo.tagtype(t) == 'global')
    if not tags:
        repo.ui.pushbuffer()
        opts = {'template': '{latesttag}\n{latesttagdistance}',
                'style': '', 'patch': None, 'git': None}
        cmdutil.show_changeset(repo.ui, repo, opts).show(ctx)
        buf = repo.ui.popbuffer()
        if buf:
            ltags, dist = buf.split('\n')
            tags = ''.join('latesttag: %s\n' % t for t in ltags.split(':'))
            tags += 'latesttagdistance: %s\n' % dist

    return base + tags


def invalidsha1(s):
    try:
        s + ''
    except Exception:
        return True
    ss = s.rsplit('_', 1)
    if len(ss) > 1:
        if not ss[1].isdigit():
            return True
        s = ss[0]
    try:
        _bin(s)
    except Exception:
        return True
    return len(s) != _sha1len


_sha1len = len(_sha1('').hexdigest())
dummyhash = '-1' * int(_sha1len / 2)
try:
    if not invalidsha1(dummyhash):
        raise RuntimeError(
            _('dummy hash %s is not recognized as being invalid') % dummyhash)
except TypeError:
    pass
_SHA_COLLISION = 42
def copyfiletosnapstore(ui, repo, src, dest, compresslevel=6, srclstat=None,
                        srcname=None, srchname=None, metadata=None):
    """copy file from src to dest, compress it with compresslevel

    The dest name is the file's name without extension as added by
    compression.

    Both src and dest are absolute paths with repo.root substracted.

    This command returns 42 in case of a sha1 collision where the
    file's sha is identical for file versions which differ in content.
    The calling function may then resolve this collision by adding
    '_<integer>' to the hash until no hash collision occurs.

    Further, the command returns the final file name including the
    used sha1, but without the extension added by compression: '.zip'.
    In case the 'dest' file name contains a sha1 of %s, it is replaced
    with the file's real sha1.

    In case 'dest' exists already and its original mtime, size, and
    sha1 (as set in the metadata) do not differ with 'src', it is
    assumed that this file has been copied already.
    """ % dummyhash
    dest_h = dest.rsplit('.', 1)[-1]
    isdummy = (dest_h == dummyhash)
    destdir = os.path.dirname(dest)
    cdest = dest+'.zip'
    srclstat = srclstat or os.lstat(src)
    if not metadata:
        ctx = repo['.']
        metadata = _metadata(repo, node=ctx.node(), ctx=ctx)
    fn = None
    fsrc = None
    fdst = None
    try:
        if not isdummy:
            if invalidsha1(dest_h):
                raise util.Abort(_('invalid hash %r for %s') % (dest_h, dest))
        if os.path.lexists(cdest):
            ui.note(_("\nalready put %r" % dest))
            cdest = _resolveshacollision(ui,
                                         dest, cdest, dest_h, src, srclstat)
            if os.path.lexists(cdest):
                return cdest[:-4]
        ui.note(_('\nput %r' % src))
        ui.flush()

        if destdir and not os.path.isdir(destdir):
            util.makedirs(destdir, mode=repo.store.createmode)

        compresslevel = int(compresslevel)
        if getattr(src, 'read', None):
            fsrc = src
            fsrc.seek(0)
        else:
            fsrc = open(src, 'rb')

        fn = util.atomictempfile(cdest, mode='wb',
                                 createmode=repo.store.createmode)
        name = srcname or src[len(repo.join('')):]
        fdst = snapStoreFile(fn, mode='w',
                             name=util.normpath(name),
                             hname=util.normpath(srchname or
                                                 hybridencode(name)),
                             compresslevel=compresslevel,
                             lstat=srclstat,
                             metadata=metadata,
                             sha1=not isdummy and dest_h)
        size = int(srclstat.st_size)
        h, s = _copyfileobj(fsrc=fsrc, fdst=fdst,
                            progress=ret_progress(ui, name, total=_kiB(size)))
        if size != s:
            raise util.Abort(_("%s: transferred bytes %s unequal file size %s")
                             % (name, s, size))
        if isdummy:
            dest = '%s.%s' % (dest.rsplit('.', 1)[0], h)
            cdest = dest + '.zip'
            fn._atomictempfile__name = fn.__name = cdest
            ui.note(_(' to %r') % dest[len(repo.join('')):])
            if os.path.lexists(cdest):
                ui.note(_(', already put'))
                fn._fp.flush()
                fn._atomictempfile__name = fn.__name = cdest = \
                    _resolveshacollision(ui, dest, cdest, h,
                                         src, srclstat)
                h = cdest[:-4].rsplit('.', 1)[-1]
        elif h != dest_h.rsplit('_', 1)[0]:
            raise util.Abort(_('sha1 of putted %r is not %s, but %s') %
                             (dest, dest_h.rsplit('_', 1)[0], h))
        fdst._setmeta(name=util.normpath(name),
                      hname=util.normpath(srchname or hybridencode(name)),
                      lstat=srclstat,
                      metadata=metadata,
                      compresslevel=compresslevel,
                      sha1=h)
        fdst.close()
        try:
            fn.rename()
        except (OSError, IOError), e:
            if not setattr(e, 'filename', None):
                e.filename = cdest
            raise
        os.chmod(cdest, (repo.store.createmode or 0777) & 0444)
        ui.note('\n')
    except Exception, e:
        ui.note('\n')
        raise util.Abort(_('failed put %r to %r: %s' % (src, dest, e)))
    finally:
        del(fn)
        _close(fsrc)
        _close(fdst)
    return cdest[:-4]


def copyfilefromsnapstore(ui, repo, src, dest):
    """copy file from src to dest, decompress it on the fly

    The src name is the file's name without extension as added by
    compression.

    Both src and dest are absolute paths (where it makes sense).
    """
    fsrc = None
    fdst = None
    name = dest
    if getattr(dest, 'write', None):
        fdst = dest
        name = getattr(fdst, 'name', getattr(fdst, 'filename', ''))
    try:
        ui.note(_('fetch %s\n') % src)
        # just fail if not existing
        try:
            fsrc = snapStoreFile(src+'.zip', 'r')
        except TypeError:
            fsrc = snapStoreFile(src, 'r')
        fsrcmeta = fsrc.meta()
        try:
            src_h = src.rsplit('.')[-1]
        except AttributeError:
            src_h = fsrcmeta['hname'].rsplit('.')[-1]
        if not fdst:
            destdir = os.path.dirname(dest)
            if destdir and not os.path.isdir(dest):
               util.makedirs(destdir)
            fdst = util.atomictempfile(name=dest, mode='wb', createmode=None)
        size = int(fsrcmeta.get('size', 0))
        h, s = _copyfileobj(fsrc=fsrc, fdst=fdst,
                            progress=ret_progress(ui, name, total=_kiB(size)))
        if size != s:
            raise util.Abort(_("%r: transferred bytes %s unequal file size %s")
                             % (src, s, size))
        eh = src_h.rsplit('_', 1)[0]
        if h != eh:
            raise util.Abort(_("sha1 of stored %r is not %r, but %r" %
                               (src, eh, h)))
        try:
            fdst.rename()
        except AttributeError:
            pass            # fdst == dest
        except (OSError, IOError), e:
            if not setattr(e, 'filename', None):
                e.filename = dest
            raise
    finally:
        _close(fsrc)
        del(fdst)
    return 0



def wrap_serve(orig, ui, repo, **opts):
    if opts.get('snap_store'):
        if opts['stdio']:
            s = snapsshserver(ui, opts['snap_store'])
            return s.serve_forever()
        else:
            if not repo:
                raise util.Abort(_('option snap-store requires (dummy) repo'))
            ui.setconfig('paths', 'snap-store', opts['snap_store'])
            ui.status(_('use snap-store: %r\n') %
                      _hidepassword(ui.expandpath('snap-store')))
            repo.snapstore.snapstoreid # aborts if snap store does not exist

    from mercurial.hgweb import hgweb_mod
    from mercurial.hgweb import webcommands
    from mercurial.hgweb import protocol
    hgweb_mod.perms.update([('snapput', 'push'), ('snapget', 'pull'),
                            ('snappush', 'push'), ('snappull', 'pull'),
                            ('snapfilestream_out', 'pull'),
                            ('snapstoreid', 'pull'),
                            ('snapused', 'pull'),
                            ('snapmetadata', 'pull'),
                            ('snapverify', 'pull'),
                            ('snapfilestream_out', 'pull')])

    def _recvfile(self, src):
        fd, tempname = tempfile.mkstemp(prefix='hg-snapput-')
        fp = os.fdopen(fd, 'wb+')
        try:
            self.getfile(fp)
        finally:
            fp.close()
        return tempname
    protocol.webproto._recvfile = _recvfile # monkeypatch

    return orig(ui, repo, **opts)



propertycache = util.propertycache
class snaplocalstore(object):
    """store for (big) file snapshots outside a Mercurial repository

    The method arguments src and dest are always file names with
    '.zip' extension, it is assumed that src and dest are
    hybridencoded.
    """
    capabilities = 'snapstore'

    def __init__(self, baseui, path, create=0):
        self.path = os.path.realpath(
            util.localpath(util.drop_scheme('file', path)))
        self.ui = baseui
        self.path = os.path.realpath(self.path)
        if not os.path.isdir(self.path):
            if create:
                try:
                    os.makedirs(self.path)
                except (OSError, IOError, Exception), e:
                    raise error.RepoError(
                        _("could not create snap store %s") % self.path)
            else:
                raise error.RepoError(_('no store at %s') % self.path)

        self.store = store.basicstore(self.path, util.opener, os.path.join)
        self.opener = self.store.opener
        self.createmode = self.store.createmode

    def url(self):
        return 'file:' + self.path

    def local(self):
        return True

    def cancopy(self):
        return self.local()

    def join(self, f):
        return os.path.join(self.path, util.localpath(f))

    @propertycache
    def snapstoreid(self):
        # socket.getfqdn is sometimes too slow
        return _sha1(socket.gethostname()+os.path.realpath(self.path)
                     ).hexdigest()

    def snapused(self):
        """return 0 if not used, 1 if any content in snap store (dir orfile)
        """
        return int(len(util.osutil.listdir(self.path)) != 0)

    def snapmetadata(self, src):
        try:
            fsrc = snapStoreFile(self.join(src+'.zip'), 'r')
        except (OSError, IOError):
            return ''
        try:
            return repr(fsrc.meta())
        finally:
            _close(fsrc)
        return

    def snapput(self, src, dest, compresslevel=6, srclstat=None, srcname=None,
                metadata=None):
        ret = copyfiletosnapstore(self.ui, self, src, self.join(dest),
                                  compresslevel=compresslevel,
                                  srclstat=srclstat,
                                  srcname=srcname,
                                  metadata=metadata)
        return util.pconvert(ret[len(self.path)+1:])

    def snapget(self, src, dest):
        return copyfilefromsnapstore(self.ui, None, self.join(src), dest)

    def snappull(self, remote, src):
        # copy or link local zip files, else stream zip files from remote
        if remote.snapstoreid == self.snapstoreid:
            return
        srcmeta = self.snapmetadata(src)
        if srcmeta and remote.snapmetadata(src) == srcmeta:
            return

        csrc = src+'.zip'
        dest = self.join(csrc)
        destdir = os.path.dirname(dest)
        if not os.path.lexists(destdir):
            util.makedirs(destdir)

        ftmp = util.mktempcopy(name=dest, emptyok=True,
                               createmode=self.store.createmode)
        os.chmod(ftmp, 0777)    # dest may already exist and is read-only

        fdest = None
        try:
            if remote.cancopy():
                os.unlink(ftmp) # 
                _copyfiles(self.ui, None, remote.join(csrc), ftmp,
                           hardlink=True)
            else:
                fsrc = remote.snapfilestream_out(src)
                l = fsrc.next()
                try:
                    size = long(l)
                except ValueError:
                    raise error.ResponseError(
                        _('snappull: unexpected response:'),  l)

                fdest = open(ftmp, 'wb')
                for chunk in fsrc:
                    fdest.write(chunk)
                fdest.flush()
                realsize = long(os.lstat(ftmp).st_size)
                if size != realsize:
                    raise util.Abort(error.RepoError(
                            _('snappull: received %s bytes instead of %s') %
                            (realsize, size)))

            if os.path.lexists(dest):
                self.ui.note(_("%s already there, check it" % src))
                dest_h = dest.rsplit('.')[-2]
                stdest = snapStoreFile(ftmp, 'r')
                try:
                    srcmeta = stdest.meta()
                    srclstat = stat_result((0, 0, 0, 1, 0, 0, srcmeta['size'],
                                            0, srcmeta['mtime'], 0))

                    if _checkshacollision(self.ui, dest, dest_h, stdest,
                                          srclstat):
                        raise util.Abort(
                            _('hash collision: remote %s and local %s have the'
                              ' same hash, but differ in content (in case'
                              ' the files are from unrelated repositories,'
                              ' you may disentangle the stores, else you may'
                              ' remove one file, or recommit one file and the'
                              ' subsequent changesets and strip the original'
                              ' commits).') % (dest, csrc))
                    return
                finally:
                    stdest.close()
            try:
                try:
                    os.chmod(ftmp, (self.createmode or 0777) & 0444)
                except OSError, e:
                    if errno.EPERM:
                        pass
                util.rename(ftmp, dest)
            except (OSError, IOError), e:
                if not setattr(e, 'filename', None):
                    e.filename = dest
                raise
        finally:
            _close(fdest)
            if os.path.lexists(ftmp):
                util.unlink(ftmp)

        try:           # just a very rudimentary check of file consistency
            stdest = snapStoreFile(dest, 'r')
            stdest.close()
        except Exception, e:
            raise util.Abort(_('corrupt file %r after pulling %s from %s: %s')
                             % (dest, csrc, remote, e))

    def snappush(self, remote, src):
        # send (zip) file to store
        return remote.snappull(remote=self, src=src)

    def snapverify(self, sname, content=False):
        csname = self.join(sname+'.zip')
        if not os.path.lexists(csname):
            return 1
        if content:
            f_h = sname.rsplit('.')[-1]
            fsrc = None
            fdst = None
            try:
                fsrc = snapStoreFile(self.join(csname), 'r')
                fdst = open(os.devnull, 'wb')
                if f_h != _copyfileobj(fsrc, fdst)[0]: # ignore size
                    return 2
            except KeyError, e:
                return 2
            finally:
                _close(fsrc)
                _close(fdst)
        return 0

    def snapfilestream_out(self, src):
        """generator for stream out of snap (zip) file in store

        First value yielded is size, all others are chunks of data."""
        fsrc = self.join(src+'.zip')
        yield '%s\n' % long(os.lstat(fsrc).st_size)
        fp = self.opener(src+'.zip', 'rb')
        try:
            for chunk in util.filechunkiter(fp):
                yield chunk
        finally:
            fp.close()



class snapsshstore(sshrepo.sshrepository):
    def validate_repo(self, ui, sshcmd, args, remotecmd):
        # same as in sshrepository.validate_repo, but without check for repo
        self.cleanup()          # clean up previous run

        cmd = '%s %s "%s serve --stdio --snap-store %s"' #
        cmd = cmd % (sshcmd, args, remotecmd, self.path)

        cmd = util.quotecommand(cmd)
        ui.note(_('running %s\n') % cmd)
        self.pipeo, self.pipei, self.pipee = util.popen3(cmd)

        # skip any noise generated by remote shell
        self._callstream('hello') # 
        r = self._callstream("between", pairs=("%s-%s" % ("0"*40, "0"*40))) # 
        lines = ["", "dummy"]
        max_noise = 500
        while lines[-1] and max_noise > 0:
            l = r.readline()
            self.readerr()
            if lines[-1] == "1\n" and l == "\n":
                break
            if l:
                ui.debug("remote: ", l)
            lines.append(l)
            max_noise -= 1
        else:
            self._abort(error.RepoError(_("no suitable response from remote hg")))

        capabilities = set()
        for l in reversed(lines):
            if l.startswith("capabilities:"):
                capabilities.update(l[:-1].split(":")[1].split())
                break
        if not 'snapstore' in capabilities:
            self._abort(error.RepoError(
                    _('expected snapstore capability, but got %s') %
                    capabilities))


    @propertycache
    def snapstoreid(self):
        return self._call('snapstoreid')

    def snapused(self):
        return int(self._call('snapused'))

    def snapmetadata(self, src):
        d = self._call('snapmetadata', src=src).strip()
        if d and d != "''":
            a = {}
            for t in d[1:-1].split(', '):
                k, v = t.split(':', 1)
                a[k] = v
            return a
        return dict()

    def snapput(self, src, dest, compresslevel=6, srclstat=None, srcname=None,
                metadata=None):
        # send file to server which puts it into store
        self.ui.debug('snapput %s\n' % ((src, dest, compresslevel, srclstat,
                                         srcname, metadata), ))
        r = self._call('snapput', src=src, dest=dest,
                       compresslevel=str(compresslevel),
                       srclstat=str(tuple(srclstat)),
                       srcname=srcname, metadata=str(metadata)).strip()
        if r and not r in ("''", 'None'):
            self._abort(error.RepoError(_('snapput failed: %s') % r))

        r = self._sendfile(src)
        if r and not r in ("''", 'None'):
            self._abort(error.RepoError(_('snapput failed: %s') % r))
        r = self._recv().strip()
        if r and not r in ("''", 'None'):
            self._abort(error.RepoError(_('snapput failed: %s') % r))

        return self._recv()

    def snapget(self, src, dest):
        # receive file from server
        self.ui.debug('snapget %s\n' % src)
        d = self._call('snapfilestream_out', src=src).strip()
        if d and not d in ("''", 'None'):
            self._abort(error.RepoError(_('snapget failed: %s') % d))
        tempname = ''
        try:
            tempname = self._recvfile(src)[:-4] # strip '.zip'
            ret = copyfilefromsnapstore(self.ui, None, tempname, dest)
        except error.RepoError, e:
            self._abort(error.RepoError(_('snapget failed: %s') % e))
        finally:
            if tempname:
                os.unlink(tempname)
        return ret

    def snappull(self, remote, src):
        # pull (zip) file from remote and send to server
        if self.ui.debugflag:
            self.ui.debug('%s: snappull %s %s\n' % (_hidepassword(self.url()),
                                                    _hidepassword(remote.url()),
                                                    src))
        if remote.snapstoreid == self.snapstoreid:
            return
        srcmeta = self.snapmetadata(src)
        if srcmeta and remote.snapmetadata(src) == srcmeta:
            return

        d = self._call('snappull',
                       remoteid=remote.snapstoreid, src=src).strip()
        if d and not d in ("''", 'None'):
            self._abort(error.RepoError(_('snappull failed: %s') % d))

        r = self._sendfile(remote.snapfilestream_out(src)).strip()
        if r and not r in ("''", 'None'):
            self._abort(error.RepoError(_('snappull failed: %s') % r))

    def snappush(self, remote, src):
        # let remote pull it
        if self.ui.debugflag:
            self.ui.debug('%s: snappush %s %s\n' % (_hidepassword(self.url()),
                                                    _hidepassword(remote.url()),
                                                    src))
        return remote.snappull(src, remote=self)

    def snapverify(self, sname, content=False):
        self.ui.debug('snapverify %s %s\n' % (sname, content))
        ret = self._call('snapverify', sname=sname, content=str(content))
        try:
            ret = int(ret)
        except:
            self._abort(error.RepoError(
                    _('snapverify: unexpected response: %s') % ret))
        return ret

    def snapfilestream_out(self, src):
        self.ui.debug('snapfilestream_out %s\n' % src)
        d = self._call('snapfilestream_out', src=src).strip()
        if d and not d in ("''", 'None'):
            self._abort(error.RepoError(_('snapfilestream_out failed: %s') % d))
        r = self._recv()
        try:
            size = long(r)
        except:
            self._abort(error.ResponseError(
                    _('snapfilestream_out: unexpected response:'), r))
        yield size

        while 1:
            buf = self._recv()
            if not buf:
                break
            yield(buf)

    def _sendfile(self, src):
        self.ui.debug('send file %s\n' % src)
        fsrc = None
        if isinstance(src, str):
            size = long(os.lstat(src).st_size)
            fsrc = open(src, 'rb')
            try:
                src = util.filechunkiter(fsrc)
            except:
                del fsrc
        else:
            size = src.next()
        try:
            self._send(str(size))
            for chunk in src:
                self._send(chunk)
            self._send('', flush=True)
        finally:
            _close(fsrc)
        return self._recv().strip()

    def _recvfile(self, src):
        self.ui.debug('receive file %s\n' % src)
        r = self._recv()
        try:
            size = long(r)
        except:
            self._abort(error.ResponseError(_('unexpected response:'), r))
        lsrc = os.path.basename(util.localpath(src)) + '.zip'
        (fd, tempname) = tempfile.mkstemp(prefix='.do_recvfile-', suffix=lsrc)
        os.close(fd)
        fdest = open(tempname, 'wb')
        try:
            while 1:
                buf = self._recv()
                if not buf:
                    break
                fdest.write(buf)

            fdest.flush()
            realsize = long(os.lstat(tempname).st_size)
            if size != realsize:
                self._abort(
                    error.RepoError(_('%s: %s bytes instead of %s received') %
                                    (src, realsize, size)))
        finally:
            fdest.close()
        return tempname



def snapstoreid(repo, proto):
    return '%s' % repo.snapstore.snapstoreid
def snapused(repo, proto):
    return '%s\n' % repo.snapstore.snapused()
def snapmetadata(repo, proto, src):
    return '%r\n' % repo.snapstore.snapmetadata(src)
def snapverify(repo, proto, sname, content):
    try:
        return '%s\n' % repo.snapstore.snapverify(sname, content=content)
    except Exception, e:
        return '%s, %s: %s\n' % (rev, sname, e)

def snapput(repo, proto, src, dest, compresslevel, srclstat, srcname, metadata):
    # receive file and put it into the store
    compresslevel = int(compresslevel)
    srclstat = stat_result(long(v) for v in srclstat[1:-1].split(', '))

    tsrc = None
    try:
        tsrc = proto._recvfile(src)
        return '%s\n' % repo.snapstore.snapput(tsrc, dest, compresslevel,
                                               srclstat, srcname, metadata)
    except Exception, e:
        return '%s to %s: %s\n' % (src, dest, e)
    finally:
        if tsrc:
            os.unlink(tsrc)

def snappull(repo, proto, remoteid, src):
    # receive (zip) file
    tsrc = None
    try:
        # We could instead open a new remote store and use
        # snapfilestream_out, however, that would require the
        # password for each file transmitted!
        tsrc = proto._recvfile(src)
        class bogusstore(object):
            snapstoreid = remoteid
            def cancopy(self):
                return True
            def join(self, f):
                return tsrc
        return '%s\n' % repo.snapstore.snappull(remote=bogusstore(), src=src)
    except Exception, e:
        return '%s: %s\n' % (src, e)
    finally:
        if tsrc:
            os.unlink(tsrc)

def snapfilestream_out(repo, proto, src):
    try:
        try:
            proto.do_snapfilestream_out(src)
            return ''
        except AttributeError:
            def streamer():
                try:
                    for chunk in repo.snapstore.snapfilestream_out(src):
                        yield chunk
                except (OSError, IOError, Exception), inst:
                    filename = getattr(inst, 'filename', '')
                    # Don't send our filesystem layout to the client
                    if (filename and
                        filename.startswith(repo.snapstore.path)):
                        filename = filename[len(repo.snapstore.path)+1:]
                        inst.filename = filename
                    yield str(inst)
            return wireproto.streamres(streamer())
    except Exception, e:
        return '%s: %s' % (src, e)



from mercurial import wireproto
wireproto.commands.update({
        'snapstoreid': (snapstoreid, ''),
        'snapused': (snapused, ''),
        'snapmetadata': (snapmetadata, 'src'),
        'snapverify': (snapverify, 'sname content'),
        'snapput': (snapput,
                    'src dest compresslevel srclstat srcname metadata'),
        'snappull': (snappull, 'remoteid src'),
        'snapfilestream_out': (snapfilestream_out, 'src')
        })


class snapsshserver(sshserver.sshserver):
    """the repo is the store"""
    caps = ['snapstore']

    def __init__(self, ui, path):
        dummyrepodir = tempfile.mkdtemp()
        try:
            repo = hg.repository(ui, dummyrepodir, create=1)
            # Creation sets a list of requirements, not a set
            repo = hg.repository(ui, dummyrepodir, create=0)
            super(snapsshserver, self).__init__(ui, repo)
            self.handlers[str] = snapsshserver.sendresponse
        finally:
            shutil.rmtree(dummyrepodir, ignore_errors=True)

        self.repo.snapstore = snaplocalstore(ui, path)

    def sendresponse(self, v):
        if v.startswith('capabilities: '):
            v = 'capabilities: %s\n' % ' '.join(self.caps)
        return super(snapsshserver, self).sendresponse(v)

    def _recvfile(self, src):
        lsrc = os.path.basename(util.localpath(src)) + '.zip'
        (fd, tempname) = tempfile.mkstemp(dir=self.repo.snapstore.path,
                                          prefix='.do_recvfile-', suffix=lsrc)

        fp = None
        try:
            fp = os.fdopen(fd, 'wb+')
            self.sendresponse('')
            size = long(self.fin.read(long(self.fin.readline())))

            try:
                self.getfile(fp)
            finally:
                _close(fp)
            realsize = long(os.lstat(tempname).st_size)
            if size != realsize:
                raise error.RepoError(_('%s bytes instead of %s received') %
                                      (realsize, size))
            self.sendresponse('')
        except (IOError, OSError, Exception), e:
            util.unlink(tempname)
            self.sendresponse(str(e))
        return tempname

    def do_snapfilestream_out(self, src):
        fsrc = None
        try:
            fsrc = self.repo.snapstore.snapfilestream_out(src)
            self.sendresponse('')
            for chunk in fsrc:
                self.sendresponse(chunk)
        except Exception, e:
            self.sendresponse(_('%s: %s') % (src, e))
        finally:
            _close(fsrc)



class snaphttpstore(httprepo.httprepository):
    def __init__(self, ui, path, create=0):
        super(snaphttpstore, self).__init__(ui, path)
        self.caps = set(['snapstore'])

    @propertycache
    def snapstoreid(self):
        try:
            return self._call('snapstoreid')
        except error.RepoError, e:
            raise util.Abort('%s\n(%s)' %
                             (e, _('snap: static http repos not supported')))

    def snapused(self):
        return int(self._call('snapused'))

    def snapmetadata(self, src):
        d = self._call('snapmetadata', src=src).strip()
        if d and d != "''":
            a = {}
            for t in d[1:-1].split(', '):
                k, v = t.split(':', 1)
                a[k] = v
            return a
        return dict()

    def snapput(self, src, dest, compresslevel=6, srclstat=None, srcname=None,
                metadata=None):
        # send file to server which puts it into store
        ret = self._sendfile('snapput',
                             src=src, dest=dest,
                             compresslevel=str(compresslevel),
                             srclstat=str(tuple(srclstat)),
                             srcname=srcname, metadata=str(metadata))
        try:
            int(ret)
        except ValueError:
            return ret
        raise error.RepoError(_('snapput: unexpected response: %s') % ret)

    def snapget(self, src, dest):
        # receive file from server
        tempname = self._recvfile('snapfilestream_out', src=src)
        try:
            return copyfilefromsnapstore(self.ui, None, tempname[:-4], dest)
        except error.RepoError, e:
            raise util.Abort(error.RepoError(_('snapget failed: %s') % e))
        finally:
            util.unlink(tempname)

    def snappush(self, remote, src):
        return remote.snappull(remote=self, src=src)

    def snappull(self, remote, src):
        # get (zip) file from remote and send it to server
        if remote.snapstoreid == self.snapstoreid:
            return
        srcmeta = self.snapmetadata(src)
        if srcmeta and remote.snapmetadata(src) == srcmeta:
            return

        g = remote.snapfilestream_out(src)
        try:
            size = long(g.next())
        except Exception, e:
            raise error.ResponseError(
                _("snapfilestream_out: unexpected response: %s") % e)
        (fd, tempname) = tempfile.mkstemp(prefix='.do_recvfile-')
        try:
            fp = os.fdopen(fd, 'wb')
            try:
                for buf in g:
                    fp.write(buf)
            finally:
                fp.close()
            realsize = long(os.lstat(tempname).st_size)
            if size != realsize:
                raise error.RepoError(_('%s bytes instead of %s received') %
                                      (realsize, size))

            r = self._sendfile('snappull', remoteid=remote.snapstoreid, src=src,
                               tempname=tempname)
            if r:
                self._abort(error.RepoError(_('snappull failed: %s') % (r,)))
        finally:
            os.unlink(tempname)

    def snapverify(self, sname, content=False):
        return int(
            self._call('snapverify', sname=sname, content=bool(content)))

    def snapfilestream_out(self, src):
        return self._callstream('snapfilestream_out', src=src).fp

    def _sendfile(self, cmd, tempname=None, **kwargs):
        if tempname:
            fp = url.httpsendfile(tempname, 'rb')
        else:
            fp = url.httpsendfile(kwargs['src'], 'rb')
        try:
            ret, output = self._call(
                 cmd, data=fp,
                 headers={'Content-Type': 'application/mercurial-0.1'},
                 **kwargs).split('\n', 1)
            for l in output.splitlines(True):
                self.ui.status(_('remote: '), l)
            if ret == 'None':
                return None
            return ret
        except socket.error, err:
            if err[0] in (errno.ECONNRESET, errno.EPIPE):
                raise util.Abort(_('%s failed: %s') % (cmd, err[1]))
            raise util.Abort(err[1])
        finally:
            fp.close()

    def _recvfile(self, cmd, src):
        lsrc = os.path.basename(util.localpath(src)) + '.zip'
        (fd, tempname) = tempfile.mkstemp(prefix='.do_recvfile-', suffix=lsrc)
        f = None
        try:
            f = self._callstream(cmd, src=src, style='raw')
            size = long(f.fp.next())
            fp = None
            try:
                fp = os.fdopen(fd, 'wb+')
                for chunk in f.fp:
                    fp.write(chunk)
            finally:
                _close(fp)
            realsize = long(os.lstat(tempname).st_size)
            if size != realsize:
                raise error.RepoError(_('%s bytes instead of %s sent') %
                                      (realsize, size))
        except:
            os.unlink(tempname)
            raise
        return tempname



snapschemes = {
    'file': snaplocalstore,
    'http': snaphttpstore,
    'https': snaphttpstore,
    'ssh': snapsshstore}

def _lookup(path):
    scheme = 'file'
    if path:
        c = path.find(':')
        if c > 0:
            scheme = path[:c]
    return snapschemes.get(scheme) or snapschemes['file']


def _samefile(src, dst):
    # Macintosh, Unix.
    if hasattr(os.path, 'samefile'):
        try:
            return os.path.samefile(src, dst)
        except OSError:
            return False

    # All other platforms: check for same pathname.
    return (os.path.normcase(os.path.abspath(src)) ==
            os.path.normcase(os.path.abspath(dst)))


def _copyfiles(ui, repo, src, dest, hardlink=None):
    """Copy a directory tree using hardlinks if possible"""

    if hardlink is None:
        destdir = os.path.dirname(dest)
        try:
            if not os.path.lexists(destdir):
                os.makedirs(destdir)
            hardlink = (os.stat(src).st_dev == os.stat(destdir).st_dev)
        except OSError, e:
            if e.errno == errno.ENOENT:
                e.filename = dest
            raise

    if os.path.isdir(src):
        if not os.path.exists(dest):
            os.mkdir(dest)
        for name, kind in util.osutil.listdir(src):
            srcname = os.path.join(src, name)
            destname = os.path.join(dest, name)
            _copyfiles(ui, repo, srcname, destname, hardlink)
    else:
        if not _samefile(src, dest):
            if hardlink:
                try:
                    util.os_link(src, dest)
                except (IOError, OSError):
                    hardlink = False
                    shutil.copy(src, dest)
            else:
                shutil.copy(src, dest)



def _failreport(ui, failed, failheader):
    ui.write('----\n')
    ui.write(failheader)
    ui.write('----\n')
    for f in failed:
        f = util.localpath(f)
        if not ui.quiet:
            e = str(failed[f])
            ui.write('%s%s\n' % (f, (e and ': '+e)))
        else:
            ui.write('%s\n' % f)
    ui.write('----\n')
    ui.write(_('%s snap files failed\n') % len(failed))


def snaptransferrer(ui, repo, revs,
                    function, failures, storemsg, verbosemsg, summarymsg,
                    remote, snap_store=None, **opts):
    """pull (push) stored snapped files from (to) url to (from) snap_store"""
    snap_store = snap_store or repo.snapstore
    failed = {}
    transferred = 0
    tried = set()
    if revs is None:
        revs = ''
    try:
        revs + []
    except TypeError:
        revs = [revs]

    for n in cmdutil.revrange(repo, revs):
        ui.progress('snaptransfer', n, unit='rev')
        ctx = repo[n]
        man = ctx.manifest()
        for f in ctx.files():
            if not (f in man and ctx[f].issnap()):
                continue
            if not remote:
                function(None, None, None) # will fail and report missing store
            elif storemsg:
                ui.write(storemsg % _hidepassword(remote.url()))
                storemsg = None

            name = snappedname(repo, ctx[f])
            if name in tried:
                continue
            tried.add(name)
            ui.note(verbosemsg % name)
            try:
                r = function(remote=remote, src=name, ctx=ctx)
                if r:
                    failed[name] = _('return status: %s') % r
                else:
                    transferred += 1
            except (IOError, OSError, Exception), e:
                failed[f] = e
    repo.snapfilemap.write()
    ui.progress('snaptransfer', None)
    if failed:
        try:
            remoteurl = remote.url()
        except AttributeError:
            remoteurl = remote
        failures(ui, failed, remoteurl, snap_store.url())
    if summarymsg and (failed or transferred):
        ui.write(summarymsg % (transferred, snap_store.url()))


def debugsnappull(ui, repo, node, url=None, snap_store=None, **opts):
    """pull stored snapped files from the specified source url into snap-store

    Pull files from the specified url to snap-store.  Only the snapped
    files of each given node/rev are pulled.

    If no url is given, or no store is at the url, the path
    snap-default is tried.  In case no snap-store is specified, the
    path snap-store is used.

    For efficiency, hardlinks are used for transfering stored snapped
    files, whenever both dest and snap_store are local and on the same
    filesystem.

    Files which could not be pulled are reported.

    If called as a hook with just one rev, all changesets whose local
    revision number is greater than or equal to the given one rev are
    checked for snapped files.  Further, if the path snap-default is
    defined, it is used instead of url.
    """
    revs = opts.pop('revs', None)
    if revs and node:
        raise util.Abort(_("please specify just one revision"))

    if not node is None:
        revs = [node]
    if not revs:
        raise util.Abort(_("please specify at least one revision"))
    storemsg = _('pull snap files from %s\n')
    summarymsg = _('%s snap files got into %s\n')
    if opts.get('hooktype'):
        if len(revs) == 1:
            revs = revs[0]+':'
        if not ui.verbose:
            storemsg = None
            summarymsg = None
        if _dirlike(url):
            url = '/'.join((url, '.hg', cachepath))
        turl = ui.expandpath('snap-default', url)
        if turl != 'snap-default':
            url = turl

    if url is None or isinstance(url, str):
        try:
            url = ui.expandpath(url)
            remote = _store(ui, repo=url,
                            path=ui.expandpath(url or 'snap-default'),
                            repo2=ui.expandpath('default'))
        except error.RepoError: # let fail later
            remote = None
    else:
        remote = url

    if snap_store:
        try:
            snap_store = _store(ui, repo,
                                ui.expandpath(snap_store or 'snap-store'))
        except TypeError:
            pass
    else:
        try:
            snap_store = repo.snapstore
        except AttributeError:
            raise util.Abort(_("There is no Mercurial repository here"
                               " (.hg not found) %r") %
                             _hidepassword(repo.url()))

    if not remote and opts.get('source') in ('unbundle', 'import', 'strip'):
        remote = snap_store

    verbosemsg = _('snap pull %s\n')
    def failures(ui, failed, store1, store2):
        msg = _('return status: %s') % 1
        failed = dict((k, str(v).replace(msg, ''))
                      for k, v in failed.iteritems())
        _failreport(ui, failed,
                    _('Files referenced by %s not in snap store %s (use'
                      ' :hg:`debugsnappull` to get them afterwards):\n') %
                    (opts['source'], (store1 or 'snap-default')))

    if remote == snap_store:
        verbosemsg = _('check referenced %s\n')
        def function(remote, src, ctx):
            if ctx is None and src is None:
                return
            elif repo:
                repo.snapfilemap.add(ctx.hex(), [src])
            return snap_store.snapverify(src, content=False)
    else:
        if not (not remote and opts.get('source') == 'unbundle'):
            def failures(ui, failed, store1, store2):
                _failreport(ui, failed,
                            _('Failed snap pulls from %s to %s:\n') % (store1,
                                                                       store2))
        if remote:
            def function(remote, src, ctx):
                if repo:
                    repo.snapfilemap.add(ctx.hex(), [src])
                return snap_store.snappull(remote, src)
        else:
            def function(remote, src, ctx):
                msg = _('no store at %s') % _hidepassword(url)
                if url.startswith('bundle:'):
                    msg += _("; remote bundle repo references snapped files,"
                             " need path 'snap-default' or 'default'"
                             " (see hg help snap)")
                elif not (url == 'snap-default' or hg.islocal(url)):
                    msg += _(', does remote hg use snap extension?')
                    repo.snapfilemap.write()
                raise util.Abort(msg)

    snaptransferrer(ui, repo, revs=revs,
                    function=function,
                    failures=failures,
                    storemsg=storemsg,
                    verbosemsg=verbosemsg,
                    summarymsg=summarymsg,
                    remote=remote,
                    snap_store=snap_store, **opts)


def debugsnappush(ui, repo, node=None, url=None, snap_store=None, **opts):
    """push stored snapped files from snap store to the specified source url

    Push files from the specified snap_store to url.  Only the snapped
    files of each given node/rev are pushed.

    If no url is given, the paths snap-default-push or snap-default
    are tried.  In case no snap_store is specified, the path
    snap-store is used.

    For efficiency, hardlinks are used for transferring stored snapped
    files, whenever both dest and snap_store are local and on the same
    filesystem.

    Files which could not be pushed are reported.

    If called as a hook with just one rev, all changesets whose local
    revision number is greater than or equal to the given one rev are
    checked for snapped files.  Further, if the paths snap-default or
    snap-default-push are defined, they are used instead of url.
    """
    revs = opts.pop('revs', None)
    if revs and node:
        raise util.Abort(_("please specify just one revision"))
    if node:
        revs = [node]
    if not revs:
        raise util.Abort(_("please specify just one revision"))
    storemsg = _('push snap files to %s\n')
    summarymsg = _('%s snap files pushed from %s\n')
    if opts.get('hooktype'):
        if len(revs) == 1:
            revs = revs[0]+':'
        if not ui.verbose:
            storemsg = None
            summarymsg = None
        if url is None or isinstance(url, str):
            turl = ui.expandpath('snap-default-push', 'snap-default')
            if (turl in ('snap-default-push', 'snap-default') and
                url and _dirlike(url)):
                turl = ui.expandpath(url)
                turl = '/'.join((turl, '.hg', cachepath))
            url = turl

    if url is None or isinstance(url, str):
        try:
            remote = _store(ui, repo=None,
                            path=ui.expandpath(url or 'snap-default-push',
                                               url or 'snap-default'))
        except error.RepoError: # let fail later
            remote = None
    else:
        remote = url

    if snap_store:
        try:
            snap_store = _store(ui, repo,
                                ui.expandpath(snap_store or 'snap-store'))
        except TypeError:
            pass
    else:
        try:
            snap_store = repo.snapstore
        except AttributeError:
            raise util.Abort(_("There is no Mercurial repository here"
                               " (.hg not found) %r") %
                             _hidepassword(repo.url()))

    def failures(ui, failed, store1, store2):
        _failreport(ui, failed,
                    _('Failed snap pushes from %s to %s:\n') % (store1, store2))
    if remote:
        def function(remote, src, ctx):
            return snap_store.snappush(remote, src)
    else:
        def function(remote, src, ctx):
            msg = _('no store at %s') % _hidepassword(url)
            if remote and remote.url().startswith('bundle:'):
                msg += _("; remote bundle repo references snapped files,"
                         " need path 'snap-default' or 'snap-default-push'"
                         " (see hg help snap)")
            elif not (url in ('snap-default', 'snap-default-push') or
                      hg.islocal(url)):
                msg += _(', does remote hg use snap extension?')
                repo.snapfilemap.write()
            raise util.Abort(msg)

    snaptransferrer(ui, repo, revs=revs,
                    function=function,
                    failures=failures,
                    storemsg=storemsg,
                    verbosemsg=_('push %s\n'),
                    summarymsg=summarymsg,
                    remote=remote, snap_store=snap_store, **opts)



def snapcache(ui, repo, *pats, **opts):
    """put all specified snapped files or all that changed into store"""
    match = opts.get('match') or cmdutil.match(repo, pats, opts)
    snap_store = repo.snapstore
    s = opts.get('status') or \
        repo.status(node1='.', node2=None, match=match,
                    ignored=False, clean=False, unknown=False)[0:2]
    ctx = repo['.']
    metadata = _metadata(repo, node=ctx.node(), ctx=ctx)
    wctx = repo[None]
    storeprinted = not ui.debugflag and snap_store.path == repo.join(cachepath)
    nfiles = len(ctx.files())           # too many, but faster
    for i, files in enumerate(s):
        for f in files:
            if not (f in wctx and wctx[f].issnap()):
                continue
            if not storeprinted:
                ui.write(_('[snap store: %s]\n') %
                         _hidepassword(snap_store.url()))
                storeprinted = True
            ui.progress('snapcache', i, f, unit='files', total=nfiles)
            fdest = snappedname(repo, wctx[f])
            fsrc = repo.wjoin(f)
            lock = repo.lock()
            try:
                fdest = snap_store.snapput(src=fsrc, dest=fdest,
                                           compresslevel=_compresslevel(ui, f),
                                           srclstat=os.lstat(fsrc),
                                           srcname=f,
                                           metadata=metadata)
            finally:
                lock.release()

            try:
                hname, h = fdest.rsplit('.', 1)
                if invalidsha1(h) or hname < 1:
                    raise ValueError
            except ValueError:
                raise util.Abort(_('wrong snapped name %r for %r') % (fdest,
                                                                      fsrc))
            repo.datacache[f] = '%s%s\n' % (snapprefix, fdest)
    ui.progress('snapcache', None)



def snapupdater(ui, repo, function, failures, verbosemsg, summarymsg,
                snap_store, storemsg=None, *pats, **opts):
    """update snapped files that are in proper state & contain their snapstr"""
    node = opts.get('node') or opts.get('parent1') or '.'
    rev = opts.get('rev')
    if rev and node:
        raise util.Abort(_("please specify just one revision"))
    if rev and not node:
        node = rev
    wctx = repo[None]
    if len(node) == 12:
        # A short hex node is first looked up in tags and branches by
        # repo.lookup.  This causes error messages with failed qpush.
        try:
            node = repo.changelog.lookup(node)
        except LookupError:
            pass
    ctxs = [repo[node]]
    snap_store = snap_store or repo.snapstore

    if not opts.get('parent2') in ('', None):
        p2 = opts['parent2']
        if len(p2) == 12:
            try:
                p2 = repo.changelog.lookup(p2)
            except LookupError:
                pass
        ctxs.append(repo[p2])
        ctxs.append(ctxs[0].ancestor(ctxs[1]))

    if pats or not repo._mfiles or opts.get('include') or opts.get('exclude'):
        m = cmdutil.match(repo, pats, opts)
    else:
        repo._mfiles.discard(None)
        m = _match.exact(repo.root, repo.getcwd(), repo._mfiles)
    failed = {}
    unclean = [set(), set(), set(), set()]
    updated = set()
    deleted = 0
    s = repo.status(node1=node, node2=opts.get('parent2'), match=m,
                    ignored=True, clean=True, unknown=False)[2:]
    if isinstance(m, _match.exact): # set here, repo.status reset method bad
        m.bad = lambda f, msg: None

    def __snappedname(repo, fctx=None):
        fp = None
        try:
            fp = repo.rwopener(fctx.path(), 'rb')
            s = repo.wwritedata(fctx.path(), fp.read())
            return snappedname(repo, s)
        finally:
            if fp:
                fp.close()
    # a merge could move snap strings from file to file
    ctxs.append(wctx)
    ms = merge.mergestate(repo)

    uncleans = opts.get('uncleans')
    def candidate(ctx, f, snappednameref):
        if not f in ms or uncleans or ms[f] != 'u':
            fp = None
            try:
                fp = repo.rwopener(f, 'rb')
                try:
                    if bool(snappedname(repo, fp.read(2*max_snapstr_len))):
                        snappednameref[0] = __snappedname
                        return True
                except util.Abort, e:
                    return False
            except (IOError, OSError), e:
                if e.errno != errno.ENOENT:
                    if not setattr(e, 'filename', None):
                        e.filename = repo.wjoin(f)
                    raise
                return False
            finally:
                if fp:
                    fp.close()

    ui.debug(_('snap update rev %s\n') %
             ', '.join('%s:%s' % (ctx.rev(), _hex(str(ctx.node())))
                       for ctx in ctxs))
    topic = 'snap' + function.func_name
    for j, ctx in enumerate(ctxs):
        man = ctx.manifest()
        for i, f in enumerate(ctx.walk(m)):
            if f in updated:
                continue
            if not (f in man and ctx[f].issnap()):
                ui.debug(_('%s: no snapped file in %s\n') % (f, ctx))
                continue
            repo.datacache.pop(f, None)
            _snappedname = [snappedname]
            if not candidate(ctx, f, _snappedname):
                if not (f in s[4] or f in s[0]): # clean, removed
                    unclean[j].add(f)
                    ui.note(_('%s: unclean snap file (rev %s)\n') %
                            (f, ctx.rev()))
                continue

            if ui.verbose or (pats and not m.exact(f)):
                ui.write(verbosemsg % f)
            if not opts.get('dry_run'):
                src = _snappedname[0](repo, ctx[f])
                dest = repo.wjoin(f)
                if ui.progress(topic, i, f, unit='files'):
                    ui.write('\n')
                try:
                    r = function(ui, repo, src=src, dest=dest)
                    if r:
                        raise Exception(_('return status: %s') % r)
                    try:
                        updated.add(f)
                    except (IOError, OSError), e:
                        if e.errno != errno.ENOENT:
                            if not setattr(e, 'filename', None):
                                e.filename = repo.wjoin(f)
                            raise
                except (IOError, OSError, Exception), e:
                    failed[repo.pathto(f)] = e
                    try:
                        os.unlink(dest)
                        deleted += 1
                    except OSError:
                        pass
                ui.progress(topic, None)
    if failed:
        failures(ui, failed, _hidepassword(snap_store.url()))
    if len(ctxs) > 1:
        unclean[0] = unclean[0].intersection(unclean[1]
                                             ).intersection(unclean[2])
        unclean[0] = unclean[0].intersection(unclean[3])
    if repo._mfiles:
        repo._mfiles.difference_update(updated)
        repo._mfiles.difference_update(unclean[0])
    if updated or deleted or unclean[0]:
        if not uncleans:
            for f in updated:
                try:
                    if (repo.dirstate[f] == 'n' and
                        repo.dirstate._map[f][2] != -2): # 
                        repo.dirstate.normal(f)
                except (IOError, OSError), e:
                    if e.errno != errno.ENOENT:
                        if not setattr(e, 'filename', None):
                            e.filename = repo.wjoin(f)
                            raise
        repo.dirstate.write()
        ui.write(summarymsg % (len(updated), deleted, len(unclean[0])))
        if (storemsg and
            (ui.debugflag or snap_store.path != repo.join(cachepath))):
            ui.write(storemsg % _hidepassword(snap_store.url()))
        if unclean[0]:
            ui.write(_("(see unclean snap files with"
                       " 'hg status -mard --snap')\n"))


def snapupdate(ui, repo, snap_store=None, *pats, **opts):
    """retrieve clean or merged snapped files

    As with all snaphooks, only snapped files are updated which are
    clean according to :hg:`st -c` or have been merged, and contain
    the same data as in the requested revision.

    If a list of files is omitted, all snap files reported by
    :hg:`snapstatus -c -r <rev>` will be updated/retrieved.

    Without -q/--quiet, the error/exception for missing files is printed.
    """
    def up(ui, repo, src, dest):
        return repo.snapstore.snapget(src=src, dest=dest)
    def failures(ui, failed, snap_store):
        _failreport(ui, failed,
                    _('Failed to retrieve files from %s:\n') % snap_store)
    storemsg = ''
    if ui.debugflag or snap_store and snap_store.path != repo.join(cachepath):
        storemsg = _(' [snap store: %s]\n')

    return snapupdater(ui, repo, function=up, failures=failures,
                       verbosemsg=_('snap update %s\n'),
                       summarymsg=_('%s snap files updated,'
                                    ' %s failed and thus deleted,'
                                    ' %s unclean or with other content\n'),
                       storemsg=storemsg,
                       snap_store=snap_store, *pats, **opts)


snapscheme = '.snap'
snapprefix = snapscheme+'://'
def snapsymlink(ui, repo, snap_store=None, *pats, **opts):
    """replace clean or merged snapped files by symlinks into given targetdir

    As with all snaphooks, only snapped files are replaced which are
    clean according to :hg:`st -c` or have been merged, *and* contain
    the same data as in the requested revision.

    The symbolic link targets are never created.  That is, one can
    create bogus symlinks which cannot be read or written to.  The
    file system typically complains then about nonexisting files,
    giving the name of the symlink file name, not the target.

    The targetdir is either taken from the option --targetdir or from
    the configured path snap-targetdir.

    Without -q/--quiet, the error/exception for missing files is printed.
    """
    if not util.checklink(repo.root):
        raise util.Abort(_('no support of symlinks in working dir filesystem'))

    targetdir = opts.get('targetdir') or ui.expandpath('snap-targetdir')
    if targetdir == 'snap-targetdir':
        if not targetdir:
            raise util.Abort(_('no targetdir given or configured'))

    def sym(ui, repo, src, dest):
        data = util.drop_scheme(snapscheme,
                                repo.wwritedata(f, repo[node][f].data()
                                                ).rstrip('\n\r'))
        data = os.path.normpath(os.path.join(targetdir, util.localpath(data)))
        repo.rwopener.audit_path(dst)
        return os.symlink(data, dest)
    def failures(ui, failed, snap_store):
        _failreport(ui, failed, _("Failed to replace snap files:\n"))

    return snapupdater(ui, repo, function=sym, failures=failures,
                       verbosemsg=_('replace %s by symlink\n'),
                       summarymsg=_('%s snap files replaced,'
                                   ' %s failed and maybe deleted,'
                                    ' %s unclean or with other content\n'),
                       snap_store=snap_store, *pats, **opts)


def snapdelete(ui, repo, snap_store=None, *pats, **opts):
    """delete clean or merged snapped files in working directory

    As with all snaphooks, only snapped files are deleted which are
    clean according to :hg:`st -c`, or have been merged, *and* contain
    the same data as in the requested revision.

    Without -q/--quiet, the error/exception for missing files is printed.
    """

    def delete(ui, repo, src, dest):
        try:
            return os.unlink(os.path.join(repo.root, util.pconvert(dest)))
        except (OSError, IOError), e:
            if (e.errno != errno.ENOENT):
                if not setattr(e, 'filename', None):
                    e.filename = ret.name
                raise

    def failures(ui, failed, snap_store):
        _failreport(ui, failed, _("Failed to delete snap files:\n"))

    return snapupdater(ui, repo, function=delete, failures=failures,
                       verbosemsg=_('delete %s\n'),
                       summarymsg=_('%s snap files deleted,'
                                   ' %s may not be deleted,'
                                    ' %s unclean or with other content\n'),
                       snap_store=snap_store, *pats, **opts)


class snapfilemap(object):
    def __init__(self, repo):
        '''map of node hash and referenced snap files added in that node

        Map is stored as {HASH}\\0{snapstr2}\\0{snapstr2}\\0\\n values
        in the .hg/snap/filemap file, with one line
        tip\\0{HASH}\\0\\n.  The same snapstr may appear for different
        node hashes as the referenced file may have been added and
        removed several times.
        '''
        self.repo = repo
        filemap = {str(nullrev): set([''])}
        if repo:
            self.path = os.path.join(repo.sharedpath, 'snap')
            self.opener = util.opener(self.path)
            self.opener.createmode = self.repo.store.createmode

            sfh = None
            try:
                sfh = self.opener('filemap', 'r')
                for line in sfh:
                    sha, refs = line.strip().split('\0', 1)
                    # no file names with '\n' or '\0' allowed
                    filemap[sha] = set(refs.split('\0')[:-1])# strip last '\0'
            except (IOError, OSError), e:
                if e.errno != errno.ENOENT:
                    if not setattr(e, 'filename', None):
                        e.filename = ret.name
                    raise
            except Exception:
                raise util.Abort(_('%s corrupt, delete it, and then recreate'
                                   ' with hg convert (see hg help snap)\n') %
                                 self.join('filemap'))
            finally:
                if sfh:
                    sfh.close()
            self.tip = filemap.pop('tip', [repo['tip'].hex()]).pop()
            self.heads = (filemap.pop('heads', None) or
                          [repo[r].hex() for r in repo.heads()])
        self.map = filemap
        try:
            self._refresh()
        except error.LockUnavailable, e:
            if e.errno != errno.EACCES:
                raise      # local pull clone without write permission

    def _refresh(self):
        if not self.repo:
            return
        repo = self.repo
        ui = self.repo.ui
        heads = [repo[r].hex() for r in repo.heads()]
        outdatedheads = set(self.heads).difference(heads)
        removedheads = set([head for head in outdatedheads if not head in repo])
        cl = repo.changelog
        newheads = [repo.lookup(h) for h in (set(heads) - set(self.heads))
                    if h in cl and not h in self.map]
        dirtyheads = set([h for h in set(heads).difference(newheads)
                          if not h in self.map])
        if self.tip != repo['tip'].hex():
            dirtyheads.add(repo['tip'].hex())
        if removedheads or newheads or dirtyheads:
            lock = repo.lock()
            try:
                if removedheads:
                    delrevs = []
                    for node in self.map:
                        if not node in repo:
                            delrevs.append(node)
                    for node in delrevs:
                        del(self.map[node])

                oldheads = [repo.lookup(h) for h in outdatedheads-removedheads]
                (nodes, outroots) = \
                 repo.changelog.nodesbetween(roots=oldheads, heads=newheads)[:2]
                nodes = set([repo[n].rev() for n in nodes])
                for head in outroots:
                    nodes.update(r for r in cmdutil.revrange(repo, [':'+head]))
                tip = -1
                if self.tip in repo:
                    tip = repo[self.tip].rev()
                for head in dirtyheads:
                    try:    # heads in repo, but not in changelog
                        nodes.update([r for r
                                      in cmdutil.revrange(repo, [':'+head])
                                      if r > tip])
                    except error.RepoLookupError:
                        continue
                for n in sorted(nodes):
                    ctx = repo[n]
                    ui.progress('snapfilemap', ctx.rev(), unit='rev')
                    try:
                        man = ctx.manifest()
                        for f in ctx.files():
                            if not (f in man and ctx[f].issnap()):
                                continue
                            name = snappedname(repo, ctx[f])
                            self.add(ctx.hex(), [name])
                    except LookupError:
                        continue
                self.tip = repo['tip'].hex()
                self.heads = heads
            finally:
                lock.release()

    def join(self, f):
        return os.path.join(self.path, f)

    def add(self, node, files):
        """assume node is full hexdigest of hash"""
        try:
            self.map[node].update(files)
        except KeyError:
            self.map[node] = set(files)

    def rollback(self):
        if os.path.exists(self.join('undo.filemap')):
            util.rename(self.join('undo.filemap'), self.join('filemap'))
            self = snapfilemap(repo=self.repo)

    def write(self):
        '''Write filemap to .hg/snap/filemap

        The format is lines of {HASH}\\0{HNAME1.HASH1}\\0{HNAME2.HASH2}\\0\\n.
        '''
        wlock = self.repo.wlock()
        try:
            self._refresh()
            self.map['tip'] = [self.tip]
            self.map['heads'] = self.heads
            filemap = self.opener('filemap', 'w', atomictemp=True)
            for n, files in self.map.iteritems():
                filemap.write('%s\0%s\0\n' % (n, '\0'.join(sorted(files))))
            filemap.rename()
            self.map.pop('tip')
            self.map.pop('heads')

            # touch 00changelog.i so hgweb reloads filemap (no lock needed)
            try:
                os.utime(self.repo.sjoin('00changelog.i'), None)
            except OSError:
                pass

        finally:
            wlock.release()

    def __ne__(self, y):
        try:
            y = y.map
        except AttributeError:
            pass
        if set(self.map) != set(y):
            return True
        for k in self.map:
            if set(self.map[k]) != set(y[k]):
                return True
        return False

    def __nonzero__(self):
        return bool(self.map)

    def __iter__(self):
        return self.map.iteritems()

    def __sub__(self, y):
        sfmap = snapfilemap(repo=None)
        sfmap.map.pop(str(nullrev))
        smap = self.map
        ymap = y.map
        for k in set(smap.iterkeys()).difference(ymap.iterkeys()):
            sfmap.add(k, smap[k])
        for k in sorted(set(smap).intersection(ymap)):
            files = smap[k] - ymap[k]
            if files:
                sfmap.add(k, files)
        return sfmap

    def __len__(self):
        """return number of referenced unique snap files"""
        if self.map:
            return (len(set(f for files in self.map.itervalues()
                            for f in files))
                    - 1) # minus empty '-1' revision
        return 0



snapstr = '%s%%s.%%s\n' % snapprefix
dummy = '%s%%s.%s' % (snapprefix, dummyhash)
def wrap_openercall(orig, issnap, slacksize, ui, repo):
    rootlen = len(repo.root)
    def wrapped(*args, **opts):
        ret = orig(*args, **opts)
        if ('w' in ret.mode) or ('a' in ret.mode):
            return ret

        if getattr(ret, 'read', None):
            if not os.path.lexists(ret.name):
                return ret
            name = ret.name[rootlen+1:]
            if isinstance(name, unicode):
                name = name.encode('utf-8')
            if issnap(name):
                if not name in repo.datacache:
                    size = int(os.fstat(ret.fileno()).st_size)
                    if (slacksize == -1 or slacksize > size):
                        devnull = fsrc = None
                        try:
                            fsrc = repo.rwopener(name, 'rb')
                            fdst = open(os.devnull, 'wb')
                            h = _copyfileobj(fsrc, fdst,
                                             ret_progress(ui, name,
                                                          total=_kiB(size)))[0]
                        finally:
                            _close(devnull)
                            _close(fsrc)
                        repo.datacache[name] = '%s%s\n' % (
                            snapprefix, hybridencode(name + '.' + h))
                    if not name in repo.datacache:
                        repo.datacache[name] = snapprefix + \
                            snappedname(repo,
                                        repo.wwritedata(name, dummy%name),
                                        plain=False) + '\n'
                datacache = repo.datacache[name]
                ret = cStringIO.StringIO(datacache)
        return ret
    for attr in dir(orig):
        if attr.startswith('__'):
            continue
        setattr(wrapped, attr, getattr(orig, attr))
    return wrapped


def makesnaplocalrepo(repo, issnap, snapmatch, slacksize):
    class snaplocalrepo(repo.__class__):
        '''A local repository where Mercurial never sees data of snapped files.

        The wopener is wrapped so that for snapfiles the data is always
        '.snap://<filename>.<sha1>\n'.  The original wopener can be
        referenced by rwopener.

        The sub method of context is wrapped so that hgsubrepos become
        snaplocalrepos.

        A commit stores the snapfiles into the path
        config.paths.snap-store if defined, else into '.hg/snap/cache'.

        If the source of a hook is 'update', 'unbundle', or 'import',
        a default snap command/hook is executed before the hook.  The
        changegroup hook first executes debugsnappull.  The update
        hook first executes the hook snapupdate if defined, else the
        function snapdelete.
        '''
        def __init__(self, repo):
            self = repo
            self.rwopener = self.wopener
            self.datacache = {} # used by wrapped self.wopener
            self.wopener = wrap_openercall(self.wopener, issnap,
                                           slacksize, self.ui, self)
            self.issnap = issnap
            self.snapmatch = snapmatch
            self._snapstore = None
            self._snapfilemap = None
            # not configurable, but 'incoming' skipped for cloning
            self._defaulthooks = {'changegrouppush': _updatesnapfilemap,
                                  'changegroupserve': _updatesnapfilemap,
                                  'outgoingpush': debugsnappush,
                                  'pretxnchangegroupunbundle': debugsnappull,
                                  'import': debugsnappull}   # acts as verify
            if os.path.isdir(self.join(cachepath)): # repo already cloned
                self._defaulthooks['changegrouppull'] = debugsnappull
            _store(self.ui, repo=self, path=self.join(cachepath), create=True)
            self._default = {'update': snapupdate}  # configurable
            self._ddefault = {'update': snapdelete} # used, if deactivated
            self._mfiles = set() # files to be updated by snapupdate hook
            self.__revs = None   # remembers revs of push call
            self.__url = ''      # remembers remote/url of push call

            repo.__class__ = snaplocalrepo

        def transaction(self, desc=None):
            if desc:
                tr = super(snaplocalrepo, self).transaction(desc)
            else:
                tr = super(snaplocalrepo, self).transaction()
            # save dirstate and snapfilemap for rollback
            try:
                ds = self.opener('snap/dirstate').read()
            except IOError:
                ds = ""
            self.opener('snap/journal.dirstate', 'w').write(ds)
            try:
                fm = self.snapfilemap.opener('filemap').read()
            except IOError:
                fm = ""
            self.snapfilemap.opener('journal.filemap', 'w').write(fm)

            def ret_wrappedafter(orig):
                def wrappedafter():
                    orig()
                    try:
                        util.rename(self.join('snap/journal.dirstate'),
                                    self.join('snap/undo.dirstate'))
                    except (OSError, IOError), e:
                        if e.errno != errno.ENOENT:
                            raise
                    try:
                        util.rename(self.snapfilemap.join('journal.filemap'),
                                    self.snapfilemap.join('undo.filemap'))
                    except (OSError, IOError), e:
                        if e.errno != errno.ENOENT:
                            raise
                return wrappedafter
            tr.after = ret_wrappedafter(tr.after)
            return tr

        def rollback(self, dryrun=False):
            ret = 0
            wlock = self.wlock()
            try:
                ret = super(snaplocalrepo, self).rollback(dryrun=dryrun)
                if not dryrun:
                    if not ret and os.path.exists('snap/undo.dirstate'):
                        util.rename(self.join('snap/undo.dirstate'),
                                    self.join('snap/dirstate'))
                    self.snapfilemap.rollback()
                return ret
            finally:
                wlock.release()

        @propertycache
        def snapfilemap(self):
            if self._snapfilemap is None:
                self._snapfilemap = snapfilemap(repo=self)
            return self._snapfilemap

        @propertycache
        def snapstore(self):
            if self._snapstore is None:
                self._snapstore = _store(self.ui, repo=self, create=False)
            return self._snapstore

        def datainfile(self, data, name):
            datalen = len(data)
            try:
                rname = os.path.join(self.root, util.pconvert(name))
                if int(os.lstat(rname).st_size) != datalen:
                    return False
            except (OSError, IOError), e:
                if e.errno == errno.ENOENT:
                    return False
                raise
            f = self.rwopener(name)
            try:
                return data == f.read(datalen+1)
            except (IOError, OSError), e:
                if not setattr(e, 'filename', None):
                    e.filename = ret.name
                raise
            finally:
                f.close()

        def file(self, f):
            flog = super(snaplocalrepo, self).file(f)
            class snapflog(flog.__class__):
                def cmp(_self, node, text):
                    try:
                        issnap = self.issnap(f)
                    except (OSError, IOError):
                        issnap = False
                    if issnap:
                        t2 = flog.read(node)
                        return t2 != text
                    return super(snapflog, _self).cmp(node, text)

                def add(_self, text, meta, transaction, link, p1=None, p2=None):
                    try:
                        issnap = self.issnap(f)
                    except (OSError, IOError):
                        issnap = self[None][f].issnap()
                    if issnap:
                        meta['snap'] = 1
                    return super(snapflog, _self).add(text, meta, transaction,
                                                      link, p1=p1, p2=p2)
            flog.__class__ = snapflog

            return flog

        def commit(self, text="", user=None, date=None, match=None,
                   force=False, editor=False, extra={}):
            # It would be nice if snapcache were called in commitctx
            # or workingctx.__init__, however, then we would have to
            # do all the matching and sanity checks again.
            if not match:
                match = _match.always(self.root, repo.getcwd())
            snapfiles = 0
            scommitted = 0
            errorfiles = []
            wlock = self.wlock()  # we may rollback this very commit
            try:
                snapcache(self.ui, self, match=match)
                ret = super(snaplocalrepo,
                            self).commit(text=text, user=user, date=date,
                                         match=match, force=force,
                                         editor=editor, extra=extra)
                if ret == None:
                    return ret

                ctx = self[ret]
                node = ctx.hex()
                for f in ctx.files():
                    scommitted += 1
                    if not (f in ctx and ctx[f].issnap()):
                        continue #
                    self.datacache.pop(f, None)
                    snapfiles += 1
                    sname = snappedname(repo, fctx=ctx[f])
                    self.snapfilemap.add(node, [sname])
                    try:
                        e = invalidsha1(sname.rsplit('.', 1)[1].rstrip('\n\r'))
                    except:
                        errorfiles.append('%s: %s' % (f, sname))
                    if e:
                        errorfiles.append('%s: %s' % (f, sname))
            finally:
                if errorfiles:
                    e = None
                    try:
                        commands.rollback(self.ui, self)
                    except Exception, e:
                        pass
                    finally:
                        wlock.release()
                    raise util.Abort(_('rolled back, snap extension commited'
                                       ' invalid snap string in files:\n----\n'
                                       ' %s\n----\n%s') %
                                     ('\n '.join(errorfiles), e))
                self.snapfilemap.write()
                wlock.release()
            if snapfiles:
                self.ui.write(_('%s files commited, %s snapfiles\n') %
                              (scommitted, snapfiles))
            return ret

        def wwrite(self, filename, data, flags):
            if not 'l' in flags and data.startswith(snapprefix):
                self._mfiles.update((None, filename))
            return super(snaplocalrepo, self).wwrite(filename, data, flags)

        def hook(self, name, throw=False, **args):
            source = args.get('source')
            snaphook = None
            snapname = ''
            name_source = '%s%s' % (name, source)
            if name_source in self._defaulthooks:
                snapname = '_internal:snap'+name_source
                snaphook = self._defaulthooks[name_source]
            elif name in self._defaulthooks:
                snapname = '_internal:snap'+name
                snaphook = self._defaulthooks[name]
            elif name in self._default:
                snapname = 'snap'+name
                snaphook = self.ui.config('hooks', snapname)
                if snaphook in ('!', ''): # deactivated by user
                    snaphook = self._ddefault.get(name)
                elif not snaphook:
                    snaphook = self._default[name]

            if snapname:
                node = args.get('node')
                if not (snaphook == debugsnappush and
                        self.__revs is None and node is None):
                    args['snap_store'] = self.snapstore
                    if self.__revs:
                        args['revs'] = self.__revs[:]
                        args['node'] = None
                    if self.__url:
                        args['url'] = self.__url
                    if snaphook:
                        self.ui.setconfig('hooks', snapname, snaphook)
                        try:
                            super(snaplocalrepo, self).hook(snapname,
                                                            throw=throw,
                                                            **args)
                        finally:
                            self.ui.setconfig('hooks', snapname, None)
                    for hname, cmd in self.ui.configitems('hooks'):
                        if (hname == snapname or # already done
                            hname.split('.', 0) != snapname or not cmd):
                            continue
                        super(snaplocalrepo, self).hook(snapname, throw=throw,
                                                        **args)
                    args.pop('snap_store')

            return super(snaplocalrepo, self).hook(name, throw=throw, **args)

        def push(self, remote, force=False, revs=None, newbranch=False):
            if revs:            # needed by debugsnappush
                ouiquiet = self.ui.quiet
                self.ui.quiet = True
                o = discovery.findoutgoing(self, remote, force=force)
                self.ui.quiet = ouiquiet
                self.__revs = [_hex(n) for n in
                               self.changelog.nodesbetween(o, revs)[0]]
                if self.__revs:
                    self.__revs.insert(0, nullid)
            self.__url = remote.url()
            try:
                return super(snaplocalrepo, self).push(remote, force=force,
                                                       revs=revs,
                                                       newbranch=newbranch)
            finally:
                self.__revs = None
                self.__url = ''

        def clone(self, remote, heads=[], stream=False):
            try:
                ret = super(snaplocalrepo, self).clone(remote, heads=heads,
                                                       stream=stream)
            finally:
                if stream and not heads and remote.capable('stream'):
                    _pullusedsnapfiles(self.ui, remote, self)
                self.__url = ''
            return ret


    if (getattr(repo, 'local', lambda: False)() and
        '.hg' in util.splitpath(repo.path) and
        not getattr(repo, 'url', lambda: '')().startswith('bundle:')):
        if (getattr(repo, 'rwopener', None) or
            getattr(repo, 'datacache', None) or
            getattr(repo, 'issnap', None)):
            raise util.Abort(_('incompatible Mercurial version'))
        snaplocalrepo(repo)
        return True
    return False



def _updatesnapfilemap(ui, repo, **opts):
    """scan repo for snapfiles, update its snapfilemap, return unique snapfiles
    """
    node = opts.get('node')
    snapfiles = set()
    fnamenode_sname = {}
    lock = repo.lock()
    try:
        if not node:
            for name, ename, size in repo.store.datafiles():
                if name[-2:] != '.i':
                    continue
                flog = repo.file(name[5:-2])    # strip data/ and .i
                fname = util.normpath(name[5:-2]) # strip data/ and .i
                for i in flog:
                    n = flog.node(i)
                    if 'snap' in flog._readmeta(n): # 
                        s = flog.read(n)
                        sname = snappedname(repo, s)
                        snapfiles.add(sname)
                        fnamenode_sname[(fname, _hex(n))] = sname
                        repo.snapfilemap.add(repo[flog.linkrev(i)].hex(),
                                             [sname])

            if repo.snapfilemap or snapfiles:
                fnamemap = {}
                for i, rev in enumerate(repo):
                    ui.progress('rev', i)
                    ctx = repo[rev]
                    for f in ctx.files():
                        if f in ctx and ctx[f].issnap():
                            try:
                                fname = fnamemap[f]
                            except KeyError:
                                fname = util.normpath(
                                    repo.file(f).indexfile[5:-2])
                                fnamemap[f] = fname

                            try:
                                sname = fnamenode_sname[(fname,
                                                         _hex(ctx.manifest()[f]))]
                                repo.snapfilemap.add(ctx.hex(), [sname])
                            except KeyError, e:
                                pass
                ui.progress('rev', None)
        else:
            for i, rev in enumerate(cmdutil.revrange(repo, [node + ':'])):
                ui.progress('rev', i)
                ctx = repo[rev]
                for f in ctx.files():
                    if f in ctx and ctx[f].issnap():
                        sname = snappedname(repo, ctx[f])
                        snapfiles.add(sname)
                        repo.snapfilemap.add(ctx.hex(), [sname])
            ui.progress('rev', None)
        repo.snapfilemap.write()
    finally:
        lock.release()

    if opts.get('hooktype'):
        return
    return snapfiles


def _pullusedsnapfiles(ui, src_repo, dest_repo, **opts):
    # We cannot just copy the snapped files even if both stores were
    # local as they may be used by other repos and thus may contain
    # files which caused sha1 collisions.  Besides, src_repo's
    # snapstore could contain files which are not necessarily
    # referenced in dest_repo.  Thus we must get a list of all used
    # snap files, or traverse all files in data store and collect what
    # snap files they reference.
    if ispatchdirrepo(src_repo) or ispatchdirrepo(dest_repo):
        return                # Ignore nested mq patch directory repos

    try:
        src_snapstore = _store(ui, repo=src_repo,
                               path=ui.expandpath('snap-default'),
                               repo2=ui.expandpath('default'))
    except error.RepoError, e:     # let fail later
        src_snapstore = None

    dest_snapstore = opts.get('snap_store', None)
    if dest_snapstore is None:
        try:
            dest_snapstore = dest_repo.snapstore
        except AttributeError:
            dest_snapstore = _store(ui, repo=dest_repo, create=True)

    nostore = False
    try:
        if (src_snapstore and
            (src_snapstore.snapstoreid == dest_snapstore.snapstoreid) and
            not src_snapstore.snapused()):
            return dest_repo.snapfilemap.write()
    except (httprepo.urllib2.HTTPError, httprepo.httplib.HTTPException,
            error.RepoError):
        nostore = True          # let fail later

    snapfiles = set()
    snapfilemap = dest_repo.snapfilemap
    if src_repo.capable('pushkey') and getattr(src_repo, 'listkeys', None):
        ui.debug(_("referenced snapfiles by pushkey snapfilemap\n"))
        src_reposnapfilemap = src_repo.listkeys('snapfilemap')
        if not src_reposnapfilemap:
            if not src_repo.url().startswith('bundle:'):
                ui.write(_('no snap extension activated for %s\n') %
                         _hidepassword(src_repo.url()))
            snapfiles = _updatesnapfilemap(ui, dest_repo)
        else:
            try:
                nullid in dest_repo
            except TypeError:
                pass
            else:
                for node, files in src_reposnapfilemap.items():
                    if node in dest_repo and not node in snapfilemap.map:
                        snapfilemap.add(node, files.split('\0'))
                        for f in files.split('\0'):
                            snapfiles.add(f)
                snapfilemap.write()
    else:
        ui.note(_('local or remote Mercurial version < 1.6, scan for'
                  ' referenced snapfiles will take some time\n'))
        snapfiles = _updatesnapfilemap(ui, dest_repo)

    if snapfiles:
        def function(remote, f):
            return dest_snapstore.snappull(remote, f)
        if src_snapstore is None or nostore:
            def function(remote, f):
                src_repo_url = ui.expandpath('snap-default')
                if src_snapstore:
                    src_repo_url = src_repo.url()
                msg = _('no store at %s') % _hidepassword(src_repo_url)
                if (src_repo_url.startswith('bundle:') or
                    src_repo.url().startswith('bundle:')):
                    msg += _("; remote bundle repo references snapped files,"
                             " need path 'snap-default' or 'default'"
                             " (see hg help snap)")
                elif nostore or src_repo_url == 'snap-default':
                    msg += ', does remote hg use snap extension?'
                raise util.Abort(msg)
        nsnapfiles = len(snapfiles)
        failed = {}
        for i, f in enumerate(snapfiles):
            ui.progress('snappull', i, item=f, total=nsnapfiles, unit='files')
            try:
                r = function(src_snapstore, f)
                if r:
                    failed[name] = _('return status: %s') % r
            except (IOError, OSError, Exception), e:
                failed[f] = e
        ui.progress('snappull', None)
        if failed:
            try:
                src_snapstore_url = src_snapstore.url()
            except AttributeError:
                src_snapstore_url = src_snapstore or 'snap-default'
            try:
                dest_snapstore_url = dest_snapstore.url()
            except AttributeError:
                dest_snapstore_url = dest_snapstore or 'snap-store'

            _failreport(ui, failed, _('Failed snap pulls from %s to %s:\n') %
                        (_hidepassword(src_snapstore_url),
                         _hidepassword(dest_snapstore_url)))


islink = os.path.islink
def ret_issnap(root, size_threshold, snapmatch):
    def issnap(f):
        if f.startswith('.hg'):
            return False
        # always called with f being relative to repo.root
        try:
            absname = os.path.join(root, util.pconvert(f))
        except AttributeError:          # no Mercurial (sub)repo
            return False
        try: # snapupdater is always called so that we'll always see whole data
            stat = os.lstat(absname)
        except OSError, e:
            if e.errno == errno.ENOENT:
                return False
            raise
        return (not islink(absname) and
                (int(stat.st_size) > size_threshold or snapmatch(f)))
    return issnap


def ispatchdirrepo(repo):
    """detect a nested patch dir repository"""
    repourl = repo.url()
    if repourl.endswith('/'):
        repourl = repourl[:-1]
    return repourl.endswith('/.hg/patches')



def reposetup(ui, repo):
    try:                        # Only local repos can snap
        if not repo.local():
            return
    except AttributeError:
        return
    if ispatchdirrepo(repo):  # Ignore nested mq patch directory repos
        repo.snapstore = None # monkeypatch
        return

    snapmatch = _snapmatch(ui, repo.root, repo.getcwd())
    size_threshold = _threshold(ui)
    try:
        slacksize = int(ui.config('snap', 'slack_factor', -1))
        if slacksize != -1:
            if slacksize < 0:
                raise ValueError
            slacksize *= size_threshold
    except ValueError:
        raise util.Abort(_('setting snap.slack_factor %s is no integer'
                           ' of -1, 0, or any integer > 0') % slacksize)

    if not makesnaplocalrepo(repo,
                             ret_issnap(repo.root, size_threshold, snapmatch),
                             snapmatch, slacksize):
        return

    def wfctxissnap(self):
        return self._repo.issnap(self.path()) # 

    def fctxissnap(self):
        if self.path().startswith('.hg') or 'l' in self.flags():
            return False
        flog = self.filelog()
        return 'snap' in flog._readmeta(self.filenode()) # 

    for cls in (context.filectx, context.workingfilectx):
        if not (getattr(cls, 'issnap', fctxissnap).func_name in
                ('fctxissnap', 'wfctxissnap')):
            raise util.Abort(_('incompatible Mercurial version, %s with %s') %
                             (cls, cls.issnap.func_name))
    context.workingfilectx.issnap = wfctxissnap # monkeypatch
    context.filectx.issnap = fctxissnap         # monkeypatch

    if context.changectx.sub.func_dict.get('__snapwrapped'):
        return

    def snapchangectx_sub(orig, self, path):
        r = orig(self, path)
        makesnaplocalrepo(r, r._repo.issnap, snapmatch, slacksize) # 
        if r._repo['tip'] == r._repo[nullid]: # not yet cloned # 
            def wrap_subpull(orig, remote, heads=None, force=False):
                ret = orig(remote, heads=heads, force=force)
                _pullusedsnapfiles(r._repo.ui, remote, r._repo)
                return ret
            extensions.wrapfunction(r._repo, 'pull', wrap_subpull)
        return r
    extensions.wrapfunction(context.changectx, 'sub', snapchangectx_sub)
    context.changectx.sub.func_dict['__snapwrapped'] = True


    def filelogsize(orig, self, rev):
        """return the size of a given revision considering any meta"""
        node = self.node(rev)
        m = self._readmeta(node)
        if m:
            return len(self.read(node))
        return revlog.revlog.size(self, rev)
    extensions.wrapfunction(filelog.filelog, 'size', filelogsize)


    def filectxcmp(orig, self, fctx):
        """compare with other file context

        returns True if different than fctx.
        """
        if (fctx._filerev is None and self._repo._encodefilterpats
            or self.issnap() or fctx.issnap() or self.size() == fctx.size()):
            return self._filelog.cmp(self._filenode, fctx.data())

        return True
    extensions.wrapfunction(context.filectx, 'cmp', filectxcmp)


    # Need two dirstate files for file size between 4 GiB - 1 to 16 EiB,
    # and also for valid mtime
    def int2seg(i):
        if i < 2**32-1:
            return None
        return i >> 32

    def seg2int(s0, s1):
        return s0 + (s1 << 32)

    def snapdirstate_write(orig, self):
        if not self._dirty:
            return
        cs = cStringIO.StringIO()
        pack = struct.pack
        write = cs.write
        write("".join(self._pl))
        headerpos = cs.tell()
        mtimes = set()
        _format = dirstate._format
        _issnap = ret_issnap(self._root, size_threshold, snapmatch) # 
        for f, e in self._map.iteritems():
            size = e[2]
            si = int2seg(size)
            if (size != -2 and
                e[0] == 'n' and
                (not si is None or _issnap(f))):
                mtime = e[3]
                if e[1:] == [0, -1, -1]:
                    stat = os.stat(self._join(f)) # 
                    size = stat.st_size
                    si = int2seg(size)
                    mtime = int(stat.st_mtime)
                    self._map[f] = (e[0], e[1], size, mtime)
                # no copymap needed, because it is in self._map already
                #               status, mode, size, mtime, length
                e = pack(_format, e[0], e[1], si or 0, mtime, len(f))
                write(e)
                write(f)
                mtimes.add(mtime)

        snapdirstate = os.path.join('snap', 'dirstate')
        if cs.tell() > headerpos:
            # Recomputing hash of snapped files is usually expensive.
            # As long as the file was last modified "simultaneously"
            # with the current write to snap/dirstate (i.e. within the
            # same second according the file-system's time
            # granularity), recreate the snap/dirstate file until the
            # modification times differ.
            st = self._opener(snapdirstate, "w", atomictemp=True) #
            now = int(util.fstat(st).st_mtime)
            while now in mtimes:
                del(st)
                st = self._opener(snapdirstate, "w", atomictemp=True) #
                now = int(util.fstat(st).st_mtime)

            st.write(cs.getvalue())
            st.rename()
        else:
            try:
                os.unlink(self._join(snapdirstate)) # 
            except OSError, e:
                if e.errno != errno.ENOENT:
                    if not setattr(e, 'filename', None):
                        e.filename = ret.name
                    raise

        warnings.filterwarnings('ignore', category=DeprecationWarning,
                                message="'l' format requires")
        try:
            ret = orig(self)
        finally:
            warnings.filterwarnings('default', category=DeprecationWarning,
                                    message="'l' format requires")

        return ret

    def snapdirstate__read(orig, self):
        ret = orig(self)
        _map = {}
        _copymap = {}                # copymap already created by orig
        snapdirstate = os.path.join('snap', 'dirstate')
        try:
            st = self._opener(snapdirstate).read() # 
        except (IOError, OSError), err:
            if err.errno != errno.ENOENT:
                if not setattr(e, 'filename', None):
                    e.filename = ret.name
                raise
            return ret
        if not st:
            return ret

        p = parsers.parse_dirstate(_map, _copymap, st)
        for f, v in _map.iteritems():
            try:
                t = list(self._map[f])
            except KeyError:
                continue
            if t[2] >= 0 and t[3] >= 0:
                t[2] = seg2int(t[2], v[2]) # size
                t[3] = v[3]                # mtime
                self._map[f] = tuple(t)

        return ret

    extensions.wrapfunction(dirstate.dirstate, 'write', snapdirstate_write)
    extensions.wrapfunction(dirstate.dirstate, '_read', snapdirstate__read)


    def wrap_repairstrip(orig, ui, repo, node, backup="all"):
        ret = orig(ui, repo, node, backup=backup)
        repo.snapfilemap.write()
        return ret
    extensions.wrapfunction(repair, 'strip', wrap_repairstrip)


    # Matt Mackell apparently uses hg diff for shelving not commited
    # changes, so we save the snapshot at each call of diff.
    if ('nosnapcache' in mdiff.diffopts.defaults):
        raise util.Abort(_('incompatible Mercurial version, %s with %s') %
                         ('mdiff.diffopts', 'nosnapcache'))

    # wrap function in patch, not class in mdiff
    def wrap_patchdiffopts(orig, ui, opts=None, untrusted=False):
        ret = orig(ui, opts=opts, untrusted=untrusted)
        if opts and opts.get('nosnapcache', None):
            ret.defaults['nosnapcache'] = True
        return ret
    extensions.wrapfunction(patch, 'diffopts', wrap_patchdiffopts)

    def wrap_patchdiff(orig, repo, node1=None, node2=None, match=None,
                       changes=None, opts=None, **kwargs):
        if opts and not opts.defaults.get('nosnapcache', False):
            if None in (node1, node2):
                if changes:
                    for files in changes[:-1]:
                        files = [repo.wjoin(f) for f in files]
                        snapcache(ui, repo, *files)
                else:
                    files = [repo.wjoin(f)
                             for f in repo.walk(match or
                                       _match.always(repo.root, repo.getcwd()))]
                    snapcache(ui, repo, *files)
        return orig(repo, node1=node1, node2=node2, match=match,
                    changes=changes, opts=opts, **kwargs)
    extensions.wrapfunction(patch, 'diff', wrap_patchdiff)

    # Only needed for mq.
    def wrap_cmdutilupdatedir(orig, ui, repo, patches, similarity=0):
        files = orig(ui, repo, patches, similarity=similarity)
        q = getattr(repo, 'mq', None)
        if q and files and q.unapplied(repo):
            # If patches are rolled back, the parents need to be reset
            # in wrap_mergeupdate
            mqtags = [(patch.node, patch.name) for patch in q.applied]
            if mqtags:
                repo.__mqparents = repo.changelog.parents(mqtags[0][0])
            orig_repoissnap = repo.issnap
            def wrapped_patchupdatedir_issnap(f):
                if orig_repoissnap(f):
                    return True
                return _containssnapstr(repo, f)
            repo.issnap = wrapped_patchupdatedir_issnap
            try:
                # This will check for snapfiles according parent and
                # snapstr in files (not that efficient)
                snapupdate(ui, repo, snap_store=None, node=None, include=files)
            finally:
                repo.issnap = orig_repoissnap
        return files
    extensions.wrapfunction(cmdutil, 'updatedir', wrap_cmdutilupdatedir)


    snappyinternalmerges = ('internal:other', 'internal:dump',
                            'internal:prompt', 'internal:local')

    def wrap_filemerge(origfn, repo, mynode, orig, fcd, fco, fca):
        if fca.issnap() or fco.issnap() or fcd.issnap():
            ui = repo.ui
            tool, tp = filemerge._picktool(repo, ui, fcd.path(), 0, 0) # 
            if not (tool in snappyinternalmerges or
                    ui.configbool("merge-tools", tool+"."+'snap', False)):
                ui.note(_('%s: snapped file not merged!\n') % fcd.path())
                return 1
        return origfn(repo, mynode, orig, fcd, fco, fca)
    extensions.wrapfunction(filemerge, 'filemerge', wrap_filemerge)

    def wrap_mergemergestate_add(orig, self, fcl, fco, fca, fd, flags):
        if fcl.issnap():
            # CAVE: Replicate merge.mergestate.add of Mercurial 1.7
            mergestore = self._repo.join('merge') # 
            fsrc = None
            fdst = None
            try: # util.copyfile would be faster, but without ui.progress
                if not os.path.lexists(mergestore):
                    util.makedirs(mergestore, self._repo.opener.createmode)
                (tfd, tempname) = tempfile.mkstemp(prefix='.merge-',
                                                   dir=mergestore)
                os.close(tfd)
                fdst = open(tempname, 'wb')
                fsrc = self._repo.rwopener(fcl.path())
                size = int(os.fstat(fsrc.fileno()).st_size)
                ui.debug(_('%s: preserve modified content\n') % fcl.path())
                h, s = _copyfileobj(fsrc, fdst, progress=\
                                     ret_progress(ui, 'preserve '+fcl.path(),
                                                  total=_kiB(size)))
                if size != s:
                    raise util.Abort(_("%s: transferred bytes %s unequal file"
                                       " size %s") % (fcl.path(), s, size))
                fdst.close()
                # resolve possible hash collision
                oh = h
                i = 0
                while os.path.lexists(os.path.join(mergestore, h)):
                    i += 1
                    h = '%s_%s' % (oh, i)
                util.rename(tempname, os.path.join(mergestore, h))
            finally:
                _close(fsrc)
                _close(fdst)
            self._state[fd] = ['u', str(h), fcl.path(), fca.path(), # 
                               _hex(fca.filenode()), fco.path(), flags]
            self._dirty = True
            return
        return orig(self, fcl, fco, fca, fd, flags)
    extensions.wrapfunction(merge.mergestate, 'add', wrap_mergemergestate_add)

    def wrap_mergemergestate_resolve(orig, self, dfile, wctx, octx):
        # CAVE: Replicate merge.mergestate.resolve of Mercurial 1.7
        if self[dfile] == 'r':
            return 0
        state, hash, lfile, afile, anode, ofile, flags = self._state[dfile] # 
        preservedname = self._repo.join('merge/' + hash) # 
        if (not dfile.startswith('.hg') and
            (dfile in wctx and wctx[dfile].issnap() or
             dfile in octx and octx[dfile].issnap() or
             ret_issnap(self._repo.root,
                        size_threshold, snapmatch)(preservedname) or
             self._repo.snapmatch(dfile))): # 
            fsrc = None
            fdst = None
            try:
                fsrc = self._repo.opener('merge/' + hash, 'r')
                fdst = self._repo.rwopener(dfile, 'w')
                size = int(os.fstat(fsrc.fileno()).st_size)
                ui.debug(_('%s: retrieve from merge/%s\n') % (dfile, hash))
                _copyfileobj(fsrc, fdst,
                             progress=ret_progress(ui, 'retrieve '+dfile,
                                                   total=_kiB(size)))
                # CAVE: Ignore hash and size of copied file, because it could
                # differ for renames
            finally:
                _close(fsrc)
                _close(fdst)

            repo.hook(name='snapupdate', throw=False, source='merge',
                      node=wctx.node() or '', parent2=octx.node(),
                      include=[dfile])

            fcd = wctx[dfile]
            fco = octx[ofile]
            fca = self._repo.filectx(afile, fileid=anode) # 
            r = filemerge.filemerge(self._repo, self._local, lfile, # 
                                    fcd, fco, fca)
            if not r:
                self.mark(dfile, 'r')
                repo.hook(name='snapupdate', throw=False, source='merge',
                          node=wctx.node() or '', parent2=octx.node(),
                          include=[dfile])
            return r
        repo.hook(name='snapupdate', throw=False, source='merge',
                  node=wctx.node() or '', parent2=octx.node(),
                  include=[dfile])
        return orig(self, dfile, wctx, octx)
    extensions.wrapfunction(merge.mergestate, 'resolve',
                            wrap_mergemergestate_resolve)

    def wrap_merge_checkunknown(orig, wctx, mctx):
        wopener = wctx._repo.wopener    # 
        if not ispatchdirrepo(wctx._repo):
            # monkeypatch
            wctx._repo.wopener = wctx._repo.rwopener                  # 
        try:
            return orig(wctx, mctx)
        finally:
            wctx._repo.wopener = wopener
    extensions.wrapfunction(merge, '_checkunknown', wrap_merge_checkunknown)

    def wrap_merge_applyupdates(orig,
                                repo, action, wctx, mctx, actx, overwrite):
        wopener = wctx._repo.wopener    # 
        if not ispatchdirrepo(wctx._repo):
            # monkeypatch
            wctx._repo.wopener = wctx._repo.rwopener
        try:
            return orig(repo, action, wctx, mctx, actx, overwrite)
        finally:
            wctx._repo.wopener = wopener
    extensions.wrapfunction(merge, 'applyupdates', wrap_merge_applyupdates)

    def wrap_mergeupdate(orig, repo, node, branchmerge, force, partial):
        try:
            p1, p2 = repo.dirstate.parents()
            cl = repo.changelog
            if (not ((p1 == p1 in cl) and (p2 == nullid or p2 in cl)) and
                getattr(repo, '__mqparents', None)):
                repo.dirstate.setparents(*repo.__mqparents)
                if p1 == node:
                    node = repo.__mqparents[0]
                elif p2 == node:
                    node = repo.__mqparents[1]
            return orig(repo, node, branchmerge, force, partial)
        except: # delete all clean snap files which still contain snapstring
            snapdelete(repo.ui, repo, snap_store=None)
            raise
    extensions.wrapfunction(merge, 'update', wrap_mergeupdate)

    mq = None
    try:
        mq = extensions.find('mq')
    except KeyError:
        pass
    if mq:
        extensions.wrapfunction(mq.queue, 'save_dirty',
                                ret_wrap_mq_queuesave_dirty(repo))
        extensions.wrapfunction(mq.queue, 'patch', wrap_mq_queuepatch)
        extensions.wrapfunction(mq.queue, 'qrepo',
                                ret_wrap_mq_queueqrepo(repo, slacksize))


def wrap_hgclone(orig, ui, source, dest=None, pull=False, rev=None,
                 update=True, stream=False, branch=None):
    src_repo, dest_repo = orig(ui, source, dest=dest, pull=pull, rev=rev,
                               update=False, stream=stream, branch=branch)
    local = getattr(dest_repo, 'local', lambda: False)()
    if not local:
        dest_repo.snapfilemap = {}
    _pullusedsnapfiles(ui, src_repo, dest_repo)
    if update and local:
        # CAVE: Replicate from hg.clone of Mercurial 1.6
        rev, checkout = hg.addbranchrevs(src_repo, src_repo,
                                         (None, branch or []), rev)
        if rev:
            checkout = src_repo.lookup(rev[0])
        if update is not True:
            checkout = update
            if src_repo.local():
                checkout = src_repo.lookup(update)

        for test in (checkout, 'default', 'tip'):
            if test is None:
                continue
            try:
                uprev = dest_repo.lookup(test)
                break
            except error.RepoLookupError:
                continue
        bn = dest_repo[uprev].branch()
        dest_repo.ui.status(_("updating to branch %s\n") % encoding.tolocal(bn))
        hg.update(dest_repo, uprev)

    return src_repo, dest_repo
extensions.wrapfunction(hg, 'clone', wrap_hgclone)


def wrap_status(orig, ui, repo, *pats, **opts):
    snapped = opts.pop('snapped', None)
    if snapped:
        orig_localrepo_status = localrepo.localrepository.status
        def snaplocalrepo_status(orig, self, node1='.', node2=None, match=None,
                                 ignored=False, clean=False, unknown=False,
                                 listsubrepos=False):
            if isinstance(node1, context.changectx):
                ctx1 = node1
            else:
                ctx1 = self[node1]
            if isinstance(node2, context.changectx):
                ctx2 = node2
            else:
                ctx2 = self[node2]

            s = orig(self, node1=node1, node2=node2, match=match,
                     ignored=ignored, clean=clean, unknown=unknown,
                     listsubrepos=listsubrepos)
            snappeds = []
            for files in s:
                snappeds.append([f for f in files
                                 if ((f in ctx1 and ctx1[f].issnap()) or
                                     (f in ctx2 and ctx2[f].issnap()) or
                                     (not (f in ctx1 or f in ctx2) and
                                      self.issnap(self.wjoin(f))))])
            return snappeds
        extensions.wrapfunction(localrepo.localrepository, 'status',
                                snaplocalrepo_status)
    try:
        return orig(ui, repo, *pats, **opts)
    finally:
        if snapped:
            localrepo.localrepository.status = orig_localrepo_status


max_snapstr_len = len(snapprefix) + store.MAX_PATH_LEN_IN_HGSTORE + 1 + _sha1len
def _containssnapstr(repo, f):
    fp = None
    try:
        fp = repo.rwopener(f, 'rb')
        data = fp.read(2 * max_snapstr_len)
    except (IOError, OSError), e:
        if not e.errno in (errno.ENOENT, errno.ELOOP):
            if fp and not setattr(e, 'filename', None):
                e.filename = fp.name
            raise
        return False
    finally:
        _close(fp)

    try:
        sname = snappedname(repo, repo.wwritedata(f, data))
    except util.Abort:
        return False
    return not invalidsha1(sname.rsplit('.', 1)[-1].rstrip('\n\r'))


def wrap_import(orig, ui, repo, patch1, *patches, **opts):
    # No option snapfiles as for convert to specify snapped files and
    # revisions explicitely, instead, user can deactivate snap any time.

    warnedaboutsnapstr = set()
    class snapimportrepo(repo.__class__):
        def file(self, f):
            flog = super(snapimportrepo, self).file(f)
            if _containssnapstr(self, f): # patch may reference a snapped file
                if not f in warnedaboutsnapstr:
                    self.ui.warn(
                        _('%s: patch apparently created snap string\n') % f)
                    warnedaboutsnapstr.add(f)
                class snapimportflog(flog.__class__):
                    def add(_self, text, meta, transaction, link, p1=None,
                            p2=None):
                        meta['snap'] = 1
                        return super(snapimportflog,
                                     _self).add(text, meta, transaction, link,
                                                p1, p2)
                    def cmp(_self, node, text):
                        t2 = _self.read(node)
                        return t2 != text
                flog.__class__ = snapimportflog
            return flog
    repo.__class__ = snapimportrepo

    # files matching snap.patterns may contain a patched snapstr
    if ui.config('snap', 'patterns', None):
        def wrap_repoissnap(orig, f):
            if _containssnapstr(f):
                return False
            return orig(f)
        extensions.wrapfunction(repo, 'issnap', wrap_repoissnap)

    if not patch1 in patches:
        patches = set((patch1,) + patches)
    return orig(ui, repo, *patches, **opts)


def wrap_verify(orig, ui, repo, **opts):
    snapfiles = opts.pop('snapfiles', None)
    snapcontents = opts.pop('snapcontents', None)
    ret = orig(ui, repo, **opts)
    _snapfiles = snapfilemap(repo=None)
    errors = 0
    if not ispatchdirrepo(repo) and (snapcontents or snapfiles):
        ui.status(_('checking %ssnap files in [%s]\n' %
		    ((snapcontents or '') and _("content of "),
		     _hidepassword(repo.snapstore.url()))))
        _verifyerrors = {0: ('%s:%s %s ' +
                             ((snapcontents or '') and _('content ')) +
                             _('OK\n')),
                         1: _('%s:%s %s missing\n'),
                         2: _('%s:%s %s corrupted\n')}

        _alreadychecked = set() # snapped file may change in flags ...
        man = repo.manifest
        _mqfirstrev = len(repo) + 1
        if getattr(repo, 'mq', None) and repo.mq.applied:
            _mqfirstrev = repo[repo.mq.applied[0].node].rev()

        _mq = getattr(repo, 'mq', [])
        nrevs = len(repo)
        for i, rev in enumerate(repo):
            ui.progress('rev', i, total=nrevs)
            ctx = repo[rev]
            ctxhex = ctx.hex()
            for f in ctx.files():
                if f in ctx and ctx[f].issnap():
                    sname = snappedname(repo, ctx[f])
                    _snapfiles.add(ctxhex, [sname])
                    if sname in _alreadychecked:
                        continue
                    _alreadychecked.add(sname)
                    r = repo.snapstore.snapverify(sname=sname,
                                                  content=snapcontents)
                    if rev >= _mqfirstrev:
                        rev = 'mq:%s' % rev
                    if r:
                        errors += 1
                        ui.warn(_verifyerrors[r] % (rev, ctxhex, sname))
                    else:
                        ui.debug(_verifyerrors[0] % (rev, ctxhex, sname))
        ui.progress('rev', None)

        filemapname = repo.snapfilemap.join('filemap')
        corruptfilemap = False
        if repo.snapfilemap and not _snapfiles:
            corruptfilemap = True
            ui.warn(_('%s: references snap files, but none in repo\n') %
                     filemapname)
        elif repo.snapfilemap != _snapfiles:
            corruptfilemap = True
            ui.warn(_('%s: references other snap files than repo\n' %
                       filemapname))
            if ui.verbose:
                ui.write(_('snap files referenced in %s, but not in repo:\n') %
                         filemapname)
                for h, files in sorted(repo.snapfilemap - _snapfiles):
                    ui.write('%s: %s\n' % (h, ', '.join(sorted(files))))
                ui.write(_('snap files referenced in repo, but not in %s:\n') %
                         filemapname)
                for h, files in sorted(_snapfiles - repo.snapfilemap):
                    ui.write('%s: %s\n' % (h, ', '.join(sorted(files))))
        if corruptfilemap:
            ui.write(_('you may delete %s and recreate with hg convert'
                       ' (see hg help snap)\n') % filemapname)
    if snapcontents or snapfiles:
        ui.status(_('%d snapped files\n') % len(_snapfiles))
    if errors:
        ui.warn(_("%d snap file errors encountered!\n") % errors)
        return 1
    return ret



def ret_snapcmdutilmake_file(repo, store, sfiles):
    class indfile(file):
        def __init__(self, fobj):
            self.f = fobj
            # only write needed
        def write(self, wholestr):
            sname = sfiles.get(wholestr)
            if sname:
                fsrc = os.path.join(store.path, sname)
                return repo.snapstore.snapget(src=fsrc, dest=self.f)
            return self.f.write(wholestr)

    def snapcmdutilmake_file(orig, repo, pat, node=None, total=None,
                             seqno=None, revwidth=None, mode='wb',
                             pathname=None):
        return indfile(orig(repo, pat, node=node, total=total, seqno=seqno,
                            revwidth=revwidth, mode=mode, pathname=pathname))
    return snapcmdutilmake_file


def wrap_cat(orig, ui, repo, file1, *pats, **opts):
    snapped = not opts.pop('nosnapped', None)
    if snapped:
        orig_cmdutil_make_file = cmdutil.make_file
        match = cmdutil.match(repo, (file1,) + pats, opts)
        if opts.get('decode'):
            decoder = repo.wwritedata
        else:
            decoder = lambda f, d: d
        ctx = repo[opts['rev']]
        man = ctx.manifest()
        sfiles= dict((decoder(f, ctx[f].data()), snappedname(repo, ctx[f]))
                     for f in ctx.walk(match) if f in man and ctx[f].issnap())
        if sfiles:
            wrapper = ret_snapcmdutilmake_file(repo, repo.snapstore, sfiles)
            extensions.wrapfunction(cmdutil, 'make_file', wrapper)
    try:
        return orig(ui, repo, file1, *pats, **opts)
    finally:
        if snapped:
            cmdutil.make_file = orig_cmdutil_make_file



def ret_snaparchiver(kind, repo, sfiles, failed, snapfiles):
    class snaparchiver(object):
        def addfile(self, name, mode, islink, data):
            sname = sfiles.get(name)
            if sname:
                tf = None
                try:
                    th, tf = tempfile.mkstemp(prefix='.ar-')
                    os.close(th)
                    try:
                        r = repo.snapstore.snapget(src=sname, dest=tf)
                        if r:
                            failed[sname] = Exception('return status: %s' % r)
                        else:
                            snapfiles[0] += 1
                        if getattr(self, 'mtime', False):
                            os.utime(tf, (self.mtime, self.mtime))
                        elif getattr(self, 'date_time', False):
                            mtime = calendar.timegm(self.date_time)
                            os.utime(tf, (mtime, mtime))
                    except (IOError, OSError, Exception), e:
                        failed[sname] = e
                    return self.copyfile(tf, name) #
                finally:
                    if tf and os.path.lexists(tf):
                        os.unlink(tf)
            return super(snaparchiver,
                         self).addfile(name, mode, islink, data) #

    class zipit(snaparchiver, archival.zipit):
        def copyfile(self, name, arcname):
            self.z.write(name, arcname)
        def done(self):
            warnings.filterwarnings('ignore', category=DeprecationWarning,
                                    message='struct integer overflow masking')
            warnings.filterwarnings('ignore', category=DeprecationWarning,
                                    message="'H' format requires")
            try:
                super(zipit, self).done()
            finally:
                warnings.filterwarnings('default', category=DeprecationWarning,
                                        message='struct integer overflow'
                                        ' masking')
                warnings.filterwarnings('default', category=DeprecationWarning,
                                        message="'H' format requires")
    class fileit(snaparchiver, archival.fileit):
        def copyfile(self, name, arcname=None):
            arcname = os.path.join(self.basedir, arcname)
            arcnamedir = os.path.dirname(arcname)
            if not os.path.lexists(arcnamedir):
                util.makedirs(arcnamedir, mode=self.opener.createmode)
            util.copyfile(name, arcname)
    class tarit(snaparchiver, archival.tarit):
        def copyfile(self, name, arcname):
            self.z.add(name, arcname)

    archivers = {
      'files': fileit,
      'tar': tarit,
      'tbz2': lambda name, mtime: tarit(name, mtime, 'bz2'),
      'tar.bz2': lambda name, mtime: tarit(name, mtime, 'bz2'),
      'tgz': lambda name, mtime: tarit(name, mtime, 'gz'),
      'uzip': lambda name, mtime: zipit(name, mtime, False),
      'zip': zipit,
    }

    try:
        return archivers[kind]
    except KeyError, e:
        raise util.Abort(_('archiver %r not supported for repositories'
                           ' with snapped files') % e.args)


def wrap_archive(orig, ui, repo, dest, **opts):
    snapped = not opts.pop('nosnapped', None)
    failed = {}
    snapfiles = [0]
    if snapped:
        kind = opts.get('type') or archival.guesskind(dest) or 'files'
        match = cmdutil.match(repo, [], opts)
        ctx = repo[opts.get('rev')]
        node = ctx.node()
        prefix = opts.get('prefix')
        _dest = cmdutil.make_filename(repo, dest, node)
        if _dest == '-' and not prefix:
            _dest = sys.stdout
            prefix = os.path.basename(repo.root) + '-%h'
        prefix = cmdutil.make_filename(repo, prefix, node)
        if kind != 'files':
            prefix = archival.tidyprefix(_dest, kind, prefix)
        man = ctx.manifest()
        sfiles = dict((prefix+f, snappedname(repo, ctx[f]))
                      for f in ctx.walk(match) if f in man and ctx[f].issnap())
        if sfiles:
            try:
                origarchiver = archival.archivers.pop(kind)
            except KeyError:
                raise util.Abort(_("unknown archive type '%s'") % kind)

            archival.archivers[kind] = ret_snaparchiver(kind, repo, sfiles,
                                                        failed, snapfiles)
            warnings.filterwarnings('ignore', category=DeprecationWarning,
                                    message='struct integer overflow masking')
            warnings.filterwarnings('ignore', category=DeprecationWarning,
                                    message="'H' format requires")
    try:
        return orig(ui, repo, dest, **opts)
    finally:
        if snapped and sfiles:
            warnings.filterwarnings('default', category=DeprecationWarning,
                                    message='struct integer overflow masking')
            warnings.filterwarnings('default', category=DeprecationWarning,
                                    message="'H' format requires")
            archival.archivers[kind] = origarchiver
            if snapfiles[0] != 0:
                ui.write(_('%s snap files archived\n') % (snapfiles[0]))
        if failed:
            _failreport(ui, failed,
                        _('failed to retrieve files from %s:\n') % store)


def wrap_revert(origr, ui, repo, *pats, **opts):
    snapped = not opts.pop('nosnapped')
    if snapped:
        if opts["date"]:
            if opts["rev"]:
                raise util.Abort(_("you can't specify a revision and a date"))
            opts["rev"] = cmdutil.finddate(ui, repo, opts["date"])
        ctx = repo[opts['rev']]
        store = repo.snapstore

        def snapwwrite(orig, filename, data, flags):
            # never called for snapped file with orig. content in working dir
            fctx = ctx[filename]
            if fctx.issnap():
                fsrc = snappedname(repo, fctx)
                dest = repo.wjoin(filename)
                ret = repo.snapstore.snapget(src=fsrc, dest=dest)
                if 'x' in flags:
                    util.set_flags(dest, False, True)
                else:
                    util.set_flags(dest, False, False)
                return ret
            return orig(filename, data, flags)
        origwwrite = extensions.wrapfunction(repo, 'wwrite', snapwwrite)
    try:
        return origr(ui, repo, *pats, **opts)
    finally:
        if snapped:
            repo.wwrite = origwwrite


def wrap_convert(orig, ui, src, dest=None, revmapfile=None, **opts):
    # checking if files are snapped at all too is considered too complicated
    _convert = extensions.find('convert')
    if _convert != hgext.convert:
        raise util.Abort(_('no snap functionality available for custom convert'
                           ' extension %s') % _convert)

    if opts.get('make_snappy') and opts.get('revert_make_snappy'):
        raise util.Abort(_('new repository can be either snappy or not snappy'))
    try:
        sourcehg = hg.repository(ui, src, False)
        del(sourcehg)
    except error.RepoError:     # No Mercurial repo, no snapped files
        if opts.get('make_snappy') or opts.get('revert_make_snappy'):
            raise util.Abort(_('snap can only convert Mercurial repositories'))
        return orig(ui, src, dest=dest, revmapfile=revmapfile, **opts)


    def getsnappedfiles(repo, files):
        _files = dict(files)
        snappedfiles = set()
        for f in _files:
            try:
                ctx = repo[_files[f]]
                if f in ctx.manifest() and ctx[f].issnap():
                    snappedfiles.add(f)
            except TypeError: # assume filemap {file: (newfile, hash)}
                ctx = repo[_files[f][1]]
                if f in ctx.manifest() and ctx[f].issnap():
                    snappedfiles.add(f)
        return snappedfiles

    def wrap_getfile(orig, self, name, rev):
        data, flags = orig(self, name, rev)
        repo = self.repo
        if repo.issnap(name):
            store = repo.snapstore
            if store.url().endswith(cachepath):
                store = _store(repo.baseui,
                               path=os.path.join(dest or src+'-hg',
                                                 '.hg', cachepath),
                               create=1)
            fctx = self.repo[rev][name]
            if fctx.issnap():
                sname = snappedname(repo, fctx)
                store.snappull(remote=repo.snapstore, src=sname)
            else:
                fsrc = cStringIO.StringIO(data)
                fdest = hybridencode(name + '.' + dummyhash)
                ctx = repo[rev]
                _flags = fctx.flags()
                mode = int('l' in _flags and 0120000 or
                           'x' in _flags and 0100755 or
                           0100644)
                atime = sum(fctx.date())
                srclstat = stat_result((mode, 0, 0, 1, 0, 0, fctx.size(),
                                        atime, atime, atime))
                metadata = _metadata(repo, node=ctx.node(), ctx=ctx)
                compresslevel = _compresslevel(repo.ui, name)
                try:
                    fdest = store.snapput(src=fsrc,
                                          dest=fdest,
                                          compresslevel=compresslevel,
                                          srclstat=srclstat,
                                          srcname=name,
                                          metadata=metadata)
                finally:
                    del fsrc
                data = '%s%s\n' % (snapprefix, fdest)
        if not flags is None:
            return data, flags
        return data


    if opts.get('make_snappy'):
        size_threshold = _threshold(ui)
        snapmatch = _snapmatch(ui, dest or src+'-hg')
        def getsnappedfiles(repo, files):
            _files = dict(files)
            snappedfiles = set()
            for f in _files:
                try:
                    try:
                        fctx = repo[_files[f]][f]
                    except TypeError:   # assume filemap {file: (newfile, hash)}
                        fctx = repo[_files[f][1]][f]

                    if (not ('l' in fctx.flags() or f.startswith('.hg')) and
                        (fctx.issnap() or
                         snapmatch(f) or
                         fctx.size() > size_threshold)):
                        snappedfiles.add(f)
                except error.LookupError, e:
                    pass            # this file has been moved
            return snappedfiles
    elif opts.get('revert_make_snappy'):
        def getsnappedfiles(repo, files):
            return set()

        def getsnappeddata(self, fctx):
            repo = self.repo
            fsrc = repo.snapstore.join(snappedname(repo, fctx))
            (th, tf) = tempfile.mkstemp(dir=self.path, prefix='.co-')
            os.close(th)
            try:
                repo.snapstore.snapget(src=fsrc, dest=tf)
                ftf = open(tf, 'rb')
                try:
                    data = ftf.read()
                    return data
                finally:
                    ftf.close()
            finally:
                os.unlink(tf)

        def wrap_getfile(orig, self, name, rev):
            try:
                fctx = self.repo[rev][name]
            except error.LookupError, err:
                raise IOError(err)
            if fctx.issnap():
                return getsnappeddata(self, fctx)
            return orig(self, name, rev)
    elif opts.get('snappedfiles'):
        f = open(opts['snappedfiles'], 'rb')
        try:
            lex = shlex(f, opts['snappedfiles'], True)
            lex.wordchars += '!@#$%^&*()-=+[]{}|;:,./<>?'
            rev = not lex.eof
            while rev != lex.eof:
                rev = lex.get_token()
                files = set()
                lineno = lex.lineno
                while lineno == lex.lineno:
                    files.add(lex.get_token())
                snappedfiles[rev] = files
        finally:
            f.close()
        if snappedfiles:
            def getsnappedfiles(repo, files):
                _files = dict(files)
                return set(f for f in _files
                           if (f in snappedfiles[_files[f]] or
                               f in snappedfiles[':']))
        else:
            ui.warn(_("no file names in --snappedfiles %r, ignore it") %
                    opts['snappedfiles'])

    def wrap_putcommit(orig, self, files, copies, parents, commit, source,
                       revmap):
        try:
            self.repo.rissnap
        except AttributeError: # should happen only once
            self.repo.rissnap = self.repo.issnap
        try:
            source.repo
        except AttributeError:
            try:                # assume filemap_source with hg base
                source.repo = source.base.repo
            except AttributeError:
                try:
                    source.repo = source.source.repo
                except AttributeError:
                    source.repo = source.source.base.repo

        try:
            source.repo.rissnap
        except AttributeError: # should happen only once
            source.repo.rissnap = source.repo.issnap
        snappedfiles = getsnappedfiles(source.repo, files)
        def cissnap(f):
            return f in snappedfiles
        self.repo.issnap = cissnap
        source.repo.issnap = cissnap
        return orig(self, files, copies, parents, commit, source, revmap)

    def wrap_after(orig, self):
        _updatesnapfilemap(ui, self.repo)
        return orig(self)

    extensions.wrapfunction(hgext.convert.hg.mercurial_sink, 'putcommit',
                            wrap_putcommit)
    extensions.wrapfunction(hgext.convert.hg.mercurial_source, 'getfile',
                            wrap_getfile)
    extensions.wrapfunction(hgext.convert.hg.mercurial_sink, 'after',
                            wrap_after)

    return orig(ui, src, dest=dest, revmapfile=revmapfile, **opts)


def wrap_record(orig, ui, repo, *pats, **opts):
    # checking if files are snapped at all too is considered too complicated
    _record = extensions.find('record')
    if _record != hgext.record:
        raise util.Abort(_('no snap functionality available for custom'
                           ' record extension %s') % _record)

    def wrap_record_utilcopyfile(orig, src, dest):
        if not (repo.issnap(src) or repo.issnap(dest)):
            orig(src, dest)
    def wrap_record_hgrevert(orig, repo, node, choose):
        def wrapped_choose(f):
            return choose(f) and not repo.issnap(f)
        return orig(repo, node, wrapped_choose)

    def ret_snapnullpatchfile(klass):
        class snapnullpatchfile(klass):
            def readlines(self, fname):
                pass
            def writelines(self, fname, lines):
                pass
            def unlink(self, fname):
                pass
            def findlines(self, l, linenum):
                return []
            def hashlines(self):
                pass
            def write_rej(self):
                pass
            def apply(self, h):
                return 0
        return snapnullpatchfile
    def wrap_patchpatchfile__init__(
        orig, ui, fname, opener, missing=False, eolmode='strict'):
        self = orig(ui, fname, opener, missing=missing, eolmode=eolmode)
        if repo.issnap(fname): # assume just one repo, no subrepos
            self.__class__ = ret_snapnullpatchfile(self.__class__)
        return self

    def wrap_patchdiff(orig, repo, node1=None, node2=None, match=None,
                       changes=None, opts=None, **kwargs):
        opts.defaults['nosnapcache'] = True
        return orig(repo, node1=node1, node2=node2, match=match,
                    changes=changes, opts=opts, **kwargs)

    orig_utilcopyfile = util.copyfile
    extensions.wrapfunction(util, 'copyfile', wrap_record_utilcopyfile)
    orig_hgrevert = hg.revert
    extensions.wrapfunction(hg, 'revert', wrap_record_hgrevert)
    orig_patchpatchfile__init__ = patch.patchfile.__init__
    extensions.wrapfunction(patch, 'patchfile',
                            wrap_patchpatchfile__init__)
    orig_patchdiff = patch.diff
    extensions.wrapfunction(patch, 'diff', wrap_patchdiff)

    try:
        return orig(ui, repo, *pats, **opts)
    finally:
        util.copyfile = orig_utilcopyfile
        hg.revert = orig_hgrevert
        patch.patchfile.__init__ = orig_patchpatchfile__init__
        patch.diff = orig_patchdiff


def wrap_hgshelveshelve(orig, ui, repo, *pats, **opts):
    try:
        return orig(ui, repo, *pats, **opts)
    except: # delete all clean snap files which still contain snapstring
        snapdelete(ui, repo, snap_store=None)
        raise
    finally:
        repo.hook(name='update', throw=False, source='unshelve')

def wrap_hgshelveunshelve(orig, ui, repo, **opts):
    def wrap_patchpatchfile__init__(
        orig, self, ui, fname, opener, missing=False, eolmode='strict'):
        orig(self, ui, fname, repo.wopener, missing=missing, eolmode=eolmode)

    orig_patchpatchfile__init__ = patch.patchfile.__init__
    extensions.wrapfunction(patch.patchfile, '__init__',
                            wrap_patchpatchfile__init__)

    try:
        return orig(ui, repo, **opts)
    finally:
        try:
            snapupdate(ui, repo, uncleans=True)
        except:
            snapdelete(ui, repo, snap_store=None)
            raise
        finally:
            patch.patchfile.__init__ = orig_patchpatchfile__init__


def wrap_extdiffsnapshot(orig, ui, repo, files, node, tmproot):
    snapcache(ui, repo, *files)
    return orig(ui, repo, files, node, tmproot)

def wrap_extdiffdodiff(orig, ui, repo, diffcmd, diffopts, pats, opts):
    revs = opts.get('rev')
    change = opts.get('change')
    do3way = '$parent2' in ' '.join(diffopts)
    if change:
        node2 = repo.lookup(change)
        node1a, node1b = repo.changelog.parents(node2)
    else:
        node1a, node2 = cmdutil.revpair(repo, revs)
        if not revs:
            node1b = repo.dirstate.parents()[1]
        else:
            node1b = nullid

    try:
        return orig(ui, repo, diffcmd, diffopts, pats, opts)
    finally:
        # 3-way merge if there are two parents
        if do3way and node1b != nullid:
            repo.hook(name='snapupdate', throw=False, source='extdiff',
                      node=node1b, parent2=node2)


def ret_wrap_mq_queuesave_dirty(repo):
    def wrap_mq_queuesave_dirty(orig, self):
        if '_pl' in repo.dirstate.__dict__:
            p1, p2 = repo.dirstate.parents()
            if p1 in repo and p2 in repo:
                repo.hook('update', parent1=_hex(p1), parent2=_hex(p2))
        ret = orig(self)
        sf = repo.snapfilemap
        if repo.mq.applied:
            try:
                sf.tip = repo[repo[self.applied[0].node].rev() - 1].hex()
            except AttributeError:
                sf.tip = repo[repo[self.applied[0].rev].rev() - 1].hex()
        sf.write()
        return ret
    return wrap_mq_queuesave_dirty

def wrap_mq_queuepatch(orig, self, repo, patchfile):
    def wrap_patchpatchfile__init__(
        orig, self, ui, fname, opener, missing=False, eolmode='strict'):
        ctx = repo['tip']
        name = repo.wjoin(fname)
        if (fname in ctx and ctx[fname].issnap() and
            os.path.lexists(name)):
            m = cmdutil.matchfiles(repo, [fname])
            # prevent dummy warning 'no changes needed to'
            if util.any(repo.status(match=m)[:4]): # mod., add., rem., del.
                util.rename(name, name+'.orig') # 
            else:
                os.unlink(name)
            commands.revert(ui, repo, fname, nosnapped=True, rev='tip',
                            date=None)
        orig(self, ui, fname, opener, missing=missing, eolmode=eolmode)

    orig_patchpatchfile__init__ = patch.patchfile.__init__
    extensions.wrapfunction(patch.patchfile, '__init__',
                            wrap_patchpatchfile__init__)

    try:
        return orig(self, repo, patchfile)
    finally:
        patch.patchfile.__init__ = orig_patchpatchfile__init__

def ret_wrap_mq_queueqrepo(repo, slacksize):
    def wrap_mq_queueqrepo(orig, self, create=False):
        qrepo = orig(self, create=create)
        if qrepo:
            makesnaplocalrepo(qrepo, repo.issnap, repo.snapmatch, slacksize)
            # CAVE: It seems util.propertycache is forgotten.
            if not qrepo.snapfilemap and repo.snapfilemap:
                qrepo.snapfilemap = repo.snapfilemap # monkeypatch
            if not qrepo.snapstore and repo.snapstore:
                qrepo.snapstore = repo.snapstore # monkeypatch
        return qrepo
    return wrap_mq_queueqrepo



def uisetup(ui):
    try:
        compresslevel = int(ui.config('snap', 'compresslevel', default=6))
        if compresslevel < 0 or compresslevel > 9:
            raise TypeError
    except ValueError:
        raise util.Abort(_("setting snap.compresslevel=%r is no integer within"
                           " 0 to 9" % compresslevel))

    entry = extensions.wrapcommand(commands.table, 'serve', wrap_serve)
    entry[1].append(('', 'snap-store', '',
                     _('also serve possibly unrelated snap store in given directory')))

    onlysnappedopt = [('', 'snapped', None,
                       _('show only snapped and to be snapped files'))]
    entry = extensions.wrapcommand(commands.table, 'status', wrap_status)
    entry[1].extend(onlysnappedopt)
    (nix, entry) = cmdutil.findcmd('diff', commands.table)
    entry[1].append(('', 'nosnapcache', None,
                     _('do not cache snap candidates, just print dummy hash')))
    extensions.wrapcommand(commands.table, 'import', wrap_import)

    entry = extensions.wrapcommand(commands.table, 'verify', wrap_verify)
    entry[1].extend([('', 'snapfiles', None,
                      _('check all snap files exist in used snap store')),
                     ('', 'snapcontents', None,
                      _('check all snap files exist in used local snap store'
                        ' and have valid content'))])

    caaropt = ('', 'nosnapped', None,
               _("retrieve data in repository, not the snapped file's data"))
    entry = extensions.wrapcommand(commands.table, 'cat', wrap_cat)
    entry[1].append(caaropt)
    entry = extensions.wrapcommand(commands.table, 'archive', wrap_archive)
    entry[1].append(caaropt)
    entry = extensions.wrapcommand(commands.table, 'revert', wrap_revert)
    entry[1].append(caaropt)

    entry = extensions.wrapcommand(hgext.convert.cmdtable, 'convert',
                                   wrap_convert)
    entry[1].extend(
        [('', 'snappedfiles', '',
          _("provide file with lines of '<rev> <snapped files>' to snap"
          ' those files changing in given rev, rev=: means all revs, e.g.,'
          ' for repairing a snappy repository converted without active'
          ' extension snap')),
         ('', 'make-snappy', None,
          _('make new Mercurial repository snappy (see :hg:`help snap`)')),
         ('', 'revert-make-snappy', None,
          _('convert snappy repository to normal Mercurial repository'))])

    rc = None
    try:
        rc = extensions.find('record')
    except KeyError:
        pass
    if rc:
        extensions.wrapcommand(rc.cmdtable, 'record', wrap_record)
        extensions.wrapfunction(rc, 'qrecord', wrap_record)

    try:
        import tortoisehg.util.hgshelve
        extensions.wrapfunction(tortoisehg.util.hgshelve, 'unshelve',
                                wrap_hgshelveunshelve)
        extensions.wrapfunction(tortoisehg.util.hgshelve, 'shelve',
                                wrap_hgshelveshelve)
    except ImportError:
        sh = None
        try:
            sh = extensions.find('hgshelve')
        except KeyError:
            pass
        if sh:
            extensions.wrapcommand(sh.cmdtable, 'unshelve',
                                   wrap_hgshelveunshelve)
            extensions.wrapcommand(sh.cmdtable, 'shelve', wrap_hgshelveshelve)

    ex = None
    try:
        ex = extensions.find('extdiff')
    except KeyError:
        pass
    if ex:
        extensions.wrapfunction(ex, 'snapshot', wrap_extdiffsnapshot)
        extensions.wrapfunction(ex, 'dodiff', wrap_extdiffdodiff)

    from mercurial import pushkey
    def listsnapfilemap(repo):
        return dict((str(k), '\0'.join(v))
                    for k,v in getattr(repo, 'snapfilemap', {}))
    def pushsnapfilemap(repo, key, old, new):
        return False
    pushkey.register('snapfilemap', pushsnapfilemap, listsnapfilemap)


cmdtable = {
    "ssymlink|slink":
        (snapsymlink,
         [('r', 'rev', '', _('revision')),
          ('', 'targetdir', '', _('link target dir'))],
         _('[[-r] REV] [--parent1 REV1 --parent2 REV2]')),
    "sha": (snapsha, commands.walkopts, _('[OPTION]... DEST')),
    "debugsnappull":
        (debugsnappull,
         [('r', 'rev', None, _('revision'))],
         _('[OPTION]... [URL] [SNAP_STORE]')),
    "debugsnappush":
        (debugsnappush,
         [('r', 'rev', None, _('revision'))],
         _('[OPTION]... [URL] [SNAP_STORE]')),
    "debugsnapdata": (
        debugsnapdata,
        [('F', 'field-separator', ' ', _('output field separator')),
         ('', 'record-separator', r'\n', _('output record separator')),
         ('0', 'print0', None, _('end records with NUL'))],
        _('[OPTION]... [FILE]...')),
}

commands.norepo += ' debugsnapdata'
commands.optionalrepo += 'debugsnappull debugsnappush'
