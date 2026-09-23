.. _ignoreconfig:

Ignoring Errors & Files
-----------------------

.. _inline_ignoring_errors:

Ignoring individual lines
^^^^^^^^^^^^^^^^^^^^^^^^^

Similar to `flake8's ignore`_, individual lines can be ignored by adding
:code:`-- noqa` to the end of the line. Additionally, specific rules can
be ignored by quoting their code or the category.

.. code-block:: sql

    -- Ignore all errors
    SeLeCt  1 from tBl ;    -- noqa

    -- Ignore rule CP02 & rule CP03
    SeLeCt  1 from tBl ;    -- noqa: CP02,CP03

    -- Ignore all parsing errors
    SeLeCt from tBl ;       -- noqa: PRS

.. note::
   Ignoring templating (``TMP``) or parsing (``PRS``) errors can lead to
   incorrect ``sqlfluff lint`` and ``sqlfluff fix`` results because SQLFluff
   may misinterpret the SQL being analysed. See :ref:`ignoring_error_types`
   for all error categories and their codes.

.. _`flake8's ignore`: https://flake8.pycqa.org/en/3.1.1/user/ignoring-errors.html#in-line-ignoring-errors

.. _inline_ignoring_ranges:

Ignoring line ranges
^^^^^^^^^^^^^^^^^^^^

Similar to `pylint's "pylint" directive"`_, ranges of lines can be ignored by
adding :code:`-- noqa:disable=<rule>[,...] | all` to the line. Following this
directive, specified rules (or all rules, if "all" was specified) will be
ignored until a corresponding `-- noqa:enable=<rule>[,...] | all` directive.

.. code-block:: sql

    -- Ignore rule AL02 from this line forward
    SELECT col_a a FROM foo -- noqa: disable=AL02

    -- Ignore all rules from this line forward
    SELECT col_a a FROM foo -- noqa: disable=all

    -- Enforce all rules from this line forward
    SELECT col_a a FROM foo -- noqa: enable=all


.. _`pylint's "pylint" directive"`: http://pylint.pycqa.org/en/latest/user_guide/message-control.html

.. _sqlfluffignore:

:code:`.sqlfluffignore`
^^^^^^^^^^^^^^^^^^^^^^^

Similar to `Git's`_ :code:`.gitignore` and `Docker's`_ :code:`.dockerignore`,
SQLFluff supports a :ref:`sqlfluffignore` file to control which files are and
aren't linted. Under the hood we use the python `pathspec library`_ which also
has a brief tutorial in their documentation.

An example of a potential :ref:`sqlfluffignore` placed in the root of your
project would be:

.. code-block:: cfg

    # Comments start with a hash.

    # Ignore anything in the "temp" path
    /temp/

    # Ignore anything called "testing.sql"
    testing.sql

    # Ignore any ".tsql" files
    *.tsql

Ignore files can also be placed in subdirectories of a path which is being
linted and the sub files will also be applied within that subdirectory.


:code:`pyproject.toml`
^^^^^^^^^^^^^^^^^^^^^^

If you use :code:`pyproject.toml` for SQLFluff configuration, you can also
ignore files and directories using ``ignore_paths`` in
``[tool.sqlfluff.core]``.

.. code-block:: toml

    [tool.sqlfluff.core]
    ignore_paths = [
        "target/",
        "supabase/migrations/*",
        "generated/*.sql",
    ]

The patterns in ``ignore_paths`` use the same matching rules as
:ref:`sqlfluffignore`.


.. _`Git's`: https://git-scm.com/docs/gitignore#_pattern_format
.. _`Docker's`: https://docs.docker.com/engine/reference/builder/#dockerignore-file
.. _`pathspec library`: https://python-path-specification.readthedocs.io/

.. _ignoring_error_types:

Ignoring types of errors
^^^^^^^^^^^^^^^^^^^^^^^^
General *categories* of errors can be ignored using the ``--ignore`` command
line option or the ``ignore`` setting in a :code:`.sqlfluff` configuration
file. The available categories and the codes shown in lint output are:

* :code:`templating` (``TMP``): the templater could not render part of the
  source SQL, for example because a template variable is undefined.
* :code:`lexing` (``LXR``): SQLFluff could not split the rendered text into
  tokens.
* :code:`parsing` (``PRS``): the tokens did not match the selected dialect's
  grammar.
* :code:`linting`: a lint rule found a violation. Each rule has its own code,
  such as ``CP01``; there is no single code for all linting violations.

For example, to ignore parsing errors for a command or a project:

.. code-block:: console

   sqlfluff lint query.sql --ignore parsing

.. code-block:: cfg

   [sqlfluff]
   ignore = parsing

Multiple categories can be separated by commas, for example
``--ignore parsing,templating``. To ignore one rule or one error on a line,
use its code with :ref:`inline_ignoring_errors`. A :ref:`sqlfluffignore` file
selects *files* by path; it does not configure error categories.
