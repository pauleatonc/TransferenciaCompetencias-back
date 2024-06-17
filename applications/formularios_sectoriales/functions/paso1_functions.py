import os

def organigrama_regional_path(instance, filename):
    ext = filename.split('.')[-1]
    region = instance.region.region if instance.region else 'SinRegion'

    competencia_nombre = 'SinCompetencia'
    if instance.formulario_sectorial and instance.formulario_sectorial.competencia:
        competencia_nombre = instance.formulario_sectorial.competencia.nombre[:30].replace('/', '-')

    new_filename = f"Organigrama-{region}-{competencia_nombre}.{ext}"
    return os.path.join('formulario_sectorial', new_filename)
