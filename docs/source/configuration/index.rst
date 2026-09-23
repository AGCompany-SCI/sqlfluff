.. _config:

Configuration
=============

Finding configuration options
-----------------------------

Start with the :ref:`defaultconfig` to see the built-in settings and their
default values. The sections below explain where to find the available values
and examples for each kind of setting:

.. list-table:: Where to find configuration options
   :header-rows: 1

   * - Section in :code:`.sqlfluff`
     - Reference
   * - :code:`[sqlfluff]`
     - :ref:`defaultconfig` for defaults and :ref:`setting_config` for file
       formats, precedence and command-line settings.
   * - :code:`[sqlfluff:rules]` and :code:`[sqlfluff:rules:<rule name>]`
     - :ref:`ruleconfig` for where rule settings go; :ref:`ruleref` for each
       rule's configurable options and allowed values.
   * - :code:`[sqlfluff:templater:jinja]` and its subsections
     - :ref:`jinja_templater` for Jinja options, context variables, macros and
       examples. Names under :code:`:context` and :code:`:macros` are supplied
       by your project rather than selected from a fixed list.
   * - :code:`[sqlfluff:layout:type:<type>]`
     - :ref:`layoutspacingconfig` for spacing and line-position values and
       how to find segment types using :code:`sqlfluff parse`.

The default configuration is a reference for *defaults*, not a list of every
possible value for each option. For example, a rule's allowed values are
documented in that rule's entry in the :ref:`ruleref`.

.. toctree::
   :maxdepth: 2

   setting_configuration
   rule_configuration
   layout
   templating/index
   ignoring_configuration
   default_configuration
