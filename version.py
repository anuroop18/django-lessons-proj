import re
import subprocess

"""
Versioning and How It Works

The root of version calculation is git's describe command.

$ git describe

will print a version, based on closest tag it finds. If the tag points to the
commit, then only the tag is shown. Otherwise, it suffixes the tag name with
the number of additional commits on top of the tagged object and the
abbreviated object name of the most recent commit.

Versioning scheme is based on
    https://setuptools.readthedocs.io/en/latest/setuptools.html#specifying-your-project-s-version

Read that doc.
In short, doc says:

   1.0.0 > 0.7.0 > 0.6.5 > 0.6.4 > 0.6.3
And
    0.6.3 > 0.6.3b1 > 0.6.3a2 > 0.6.3a1
And
    0.6.3a1 > 0.6.3a1.dev83 > 0.6.3a1.dev82 > 0.6.3a1.dev1

    (post release)   (release)   (pre release)
    0.6.3-1        >   0.6.3   >  0.6.3.dev1
"""


def get_version():
    """
    Any tag that contains 'dev' is a development branch tag:

        0.6.1.dev34, 0.7.3a1.dev35

    Example of master tags/versions:

        0.6.3, 0.6.4a1, 0.7.0

    Master don't contain 'dev' part.
    POST release (versions with dash) are NOT supported. Just increment
    the version
    I would like to have support for that, but setuptools will
    normalize the version to X.Y.Z.post<num>

    This function will normalize git describe output to above
    versioning scheme:

        X.Y.Z.dev-<num>-<hash> => X.Y.Z.dev<num>

        X.Y.Z              =>  X.Y.Z

    """
    describe = subprocess.check_output(["git", "describe"]).strip()
    desc = describe.decode('ascii')
    m = re.search("([\w\.]+)", desc)
    vers = m.group(0) or ""

    m2 = re.search("\-(?P<order>\d+)\-", desc)
    if m2:
        order = m2.group('order') or ""
    else:
        order = ""

    if "dev" in vers:
        # becase tag is 0.7.0.dev and order is 13
        # result will be ex 0.7.0.dev13
        result = "{}{}".format(vers, order)
    elif len(order) > 0:
        # because tag is 0.7.0 and order is, say, 13
        # result will be ex 0.7.0.p13
        result = "{}.{}".format(vers, order)
    else:  # there is no dev and there is no order
        result = vers

    return result
