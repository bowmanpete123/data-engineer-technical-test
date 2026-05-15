{% macro test_chronological_order(model, column_name, column_end) %}
    select *
    from {{ model }}
    where {{ column_end }} < {{ column_name }}
{% endmacro %}
