'''gettext helper for PyWheel's internal use.

.. note::

    Internal use only.

'''
# This file is part of PyWheel.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under GNU GPLv3. See COPYING.txt for details.
import gettext

t = gettext.translation('pywheel', fallback=True)
_ = t.lgettext
__all__ = ('_',)
