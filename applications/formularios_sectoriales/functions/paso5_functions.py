from django.db.models import Sum


@staticmethod
def verificar_y_eliminar_resumen(subtitulo_id, formulario_sectorial_id, modelo_costos_directos, modelo_costos_indirectos, modelo_resumen_costos, modelo_evolucion, modelo_variacion):
    existen_directos = modelo_costos_directos.objects.filter(
        item_subtitulo__subtitulo_id=subtitulo_id,
        formulario_sectorial_id=formulario_sectorial_id
    ).exists()

    existen_indirectos = modelo_costos_indirectos.objects.filter(
        item_subtitulo__subtitulo_id=subtitulo_id,
        formulario_sectorial_id=formulario_sectorial_id
    ).exists()

    # Solo eliminar el resumen si no hay registros ni en CostosDirectos ni en CostosIndirectos
    if not existen_directos and not existen_indirectos:

        # Eliminar Resumen por Subtitulo
        modelo_resumen_costos.objects.filter(
            subtitulo_id=subtitulo_id,
            formulario_sectorial_id=formulario_sectorial_id
        ).delete()

        # Eliminar Evolucion por Subtitulo
        modelo_evolucion.objects.filter(
            subtitulo_id=subtitulo_id,
            formulario_sectorial_id=formulario_sectorial_id
        ).delete()


        # Eliminar Variacion por Subtitulo
        modelo_variacion.objects.filter(
            subtitulo_id=subtitulo_id,
            formulario_sectorial_id=formulario_sectorial_id
        ).delete()