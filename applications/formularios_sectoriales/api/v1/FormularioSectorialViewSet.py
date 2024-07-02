from django.http import HttpResponse, Http404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from applications.formularios_sectoriales.models import (
    FormularioSectorial, MarcoJuridico, OrganigramaRegional, FlujogramaCompetencia
)
from applications.users.permissions import IsSUBDEREOrSuperuser
from .serializers import (
    FormularioSectorialDetailSerializer,
    Paso1Serializer,
    Paso2Serializer,
    Paso3GeneralSerializer,
    Paso4GeneralSerializer,
    Paso5GeneralSerializer,
    ResumenFormularioSerializer,
    ObservacionesSubdereSerializer,
    MarcoJuridicoSerializer
)


def manejar_formularios_pasos(request, formulario_sectorial, serializer_class):
    if request.method == 'PATCH':
        print("Datos recibidos para PATCH:", request.data)

        serializer = serializer_class(formulario_sectorial, data=request.data, partial=True,
                                      context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print("Errores de validación:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:  # GET

        serializer = serializer_class(formulario_sectorial, context={'request': request})
        return Response(serializer.data)


def es_usuario_autorizado_para_sector(request, formulario_sectorial):
    usuario = request.user
    competencia = formulario_sectorial.competencia

    # Verifica si el usuario es un "Usuario Sectorial".
    es_usuario_sectorial = usuario.groups.filter(name='Usuario Sectorial').exists()

    # Verifica si el usuario pertenece al mismo sector que el formulario.
    mismo_sector = usuario.sector == formulario_sectorial.sector if usuario.sector else False

    # Verifica si el usuario está asignado específicamente a la competencia como usuario sectorial.
    es_usuario_sectorial_de_competencia = competencia.usuarios_sectoriales.filter(id=usuario.id).exists()

    # El usuario debe ser un usuario sectorial, pertenecer al mismo sector que el formulario,
    # y estar asignado específicamente a la competencia como usuario sectorial.
    return es_usuario_sectorial and mismo_sector and es_usuario_sectorial_de_competencia


def manejar_permiso_patch(request, formulario_sectorial, serializer_class):
    """
    Maneja los permisos para operaciones PATCH y la serialización.
    """
    if request.method == 'PATCH':
        if not es_usuario_autorizado_para_sector(request, formulario_sectorial):
            return Response({"detail": "No autorizado para editar este formulario sectorial."},
                            status=status.HTTP_403_FORBIDDEN)

        return manejar_formularios_pasos(request, formulario_sectorial, serializer_class)

    return manejar_formularios_pasos(request, formulario_sectorial, serializer_class)


class FormularioSectorialViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar las operaciones CRUD de un Formulario Sectorial.
    Ofrece Creación, actualización, detalle y eliminación de Formularios.
    """
    queryset = FormularioSectorial.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        # Selecciona el serializer adecuado en función de la acción
        if self.action == 'retrieve':
            return FormularioSectorialDetailSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        """
        Devuelve las clases de permisos de instancia para la acción solicitada.
        """
        if self.action == 'create':
            permission_classes = [IsSUBDEREOrSuperuser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        Detalle de Formulario Sectorial

        Devuelve el detalle de un formulario sectorial específico.
        Acceso para usuarios autenticados.
        """
        competencia = self.get_object()
        serializer = self.get_serializer(competencia)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'patch'], url_path='paso-1')
    def paso_1(self, request, pk=None):
        """
        API Paso 1 - Descripción de la Institución de Formulario Sectorial

        Con GET devuelve el detalle de todos los campos.

        Mediante PATCH se pueden editar los siguientes campos:

        "p_1_1_ficha_descripcion_organizacional": {
            "denominacion_organismo": "",
            "forma_juridica_organismo": "",
            "descripcion_archivo_marco_juridico": "",
            "mision_institucional": "",
            "informacion_adicional_marco_juridico": ""
        },
        "p_1_2_organizacion_institucional": {
            "organigrama_nacional": "",
            "descripcion_archivo_organigrama_regional": ""
        },
        "p_1_3_marco_regulatorio_y_funcional_competencia": {
            "identificacion_competencia": "",
            "fuentes_normativas": "",
            "territorio_competencia": "",
            "enfoque_territorial_competencia": "",
            "ambito": "",
            "posibilidad_ejercicio_por_gobierno_regional": "",
            "organo_actual_competencia": ""
        }
        """
        formulario_sectorial = self.get_object()
        return manejar_permiso_patch(request, formulario_sectorial, Paso1Serializer)

    @action(detail=True, methods=['get', 'patch'], url_path='paso-2')
    def paso_2(self, request, pk=None):
        formulario_sectorial = self.get_object()
        return manejar_permiso_patch(request, formulario_sectorial, Paso2Serializer)

    @action(detail=True, methods=['get', 'patch'], url_path='paso-3')
    def paso_3(self, request, pk=None):
        formulario_sectorial = self.get_object()
        return manejar_permiso_patch(request, formulario_sectorial, Paso3GeneralSerializer)

    @action(detail=True, methods=['get', 'patch'], url_path='paso-4')
    def paso_4(self, request, pk=None):
        formulario_sectorial = self.get_object()
        return manejar_permiso_patch(request, formulario_sectorial, Paso4GeneralSerializer)

    @action(detail=True, methods=['get', 'patch'], url_path='paso-5')
    def paso_5(self, request, pk=None):
        formulario_sectorial = self.get_object()
        return manejar_permiso_patch(request, formulario_sectorial, Paso5GeneralSerializer)

    @action(detail=True, methods=['get', 'patch'], url_path='resumen')
    def resumen(self, request, pk=None):
        """
        API para obtener o actualizar el resumen de todos los pasos del Formulario Sectorial
        """
        formulario_sectorial = self.get_object()

        if request.method == 'PATCH':
            # Aquí manejas el PATCH utilizando la lógica de permisos y actualización
            return manejar_permiso_patch(request, formulario_sectorial, ResumenFormularioSerializer)

        # Si el método es GET, simplemente serializas y retornas los datos como antes
        serializer = ResumenFormularioSerializer(formulario_sectorial)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'patch'], url_path='observaciones-subdere-sectorial')
    def observaciones_sectoriales(self, request, pk=None):
        formulario_sectorial = self.get_object()
        competencia = formulario_sectorial.competencia

        # Verifica si el usuario es un usuario SUBDERE autorizado para la competencia del formulario sectorial
        if request.method == 'PATCH' and not request.user in competencia.usuarios_subdere.all():
            return Response({"detail": "No autorizado para editar las observaciones de SUBDERE."},
                            status=status.HTTP_403_FORBIDDEN)

        return manejar_formularios_pasos(request, formulario_sectorial, ObservacionesSubdereSerializer)

    @action(detail=True, methods=['patch'], url_path='update-marco-juridico',
            parser_classes=(MultiPartParser, FormParser))
    def update_marco_juridico(self, request, pk=None):
        """
        Un endpoint dedicado para actualizar el documento de un MarcoJuridico específico
        o crear uno nuevo si no se proporciona marco_juridico_id.

        Se deben agregar en el body dos keys, marco_juridico_id: el valor del ID y documento: el archivo a subir. Si se
        proporciona marco_juridico_id, el endpoint actualiza el documento existente. Si no se proporciona
        marco_juridico_id, el endpoint crea un nuevo MarcoJuridico.
        """
        formulario_sectorial = self.get_object()

        # Verificar permisos del usuario
        if not es_usuario_autorizado_para_sector(request, formulario_sectorial):
            return Response({"detail": "No autorizado para editar este documento."},
                            status=status.HTTP_403_FORBIDDEN)

        marco_juridico_id = request.data.get('marco_juridico_id')
        documento_file = request.FILES.get('documento')

        if not documento_file:
            return Response({"error": "Documento es requerido."},
                            status=status.HTTP_400_BAD_REQUEST)

        if marco_juridico_id:
            # Intenta actualizar un MarcoJuridico existente
            try:
                marco_juridico = MarcoJuridico.objects.get(id=marco_juridico_id,
                                                           formulario_sectorial=formulario_sectorial)
            except MarcoJuridico.DoesNotExist:
                return Response({"error": "MarcoJuridico no encontrado."}, status=status.HTTP_404_NOT_FOUND)

            marco_juridico.documento = documento_file
            marco_juridico.save()

            return Response({"mensaje": "Documento actualizado con éxito."})
        else:
            # Crea un nuevo MarcoJuridico si no se proporciona ID
            marco_juridico = MarcoJuridico.objects.create(
                formulario_sectorial=formulario_sectorial,
                documento=documento_file
            )

            return Response({"mensaje": "Documento creado con éxito.", "marco_juridico_id": marco_juridico.id},
                            status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='update-flujograma-competencia',
        parser_classes=(MultiPartParser, FormParser))
    def update_flujograma_competencia(self, request, pk=None):
        """
        Un endpoint dedicado para actualizar el documento de un FlujogramaCompetencia específico
        o crear uno nuevo si no se proporciona flujograma_competencia_id.

        Se deben agregar en el body dos keys, flujograma_competencia_id: el valor del ID y documento: el archivo a subir.
        Si se proporciona flujograma_competencia_id, el endpoint actualiza el documento existente. Si no se proporciona
        flujograma_competencia_id, el endpoint crea un nuevo FlujogramaCompetencia.
        """
        formulario_sectorial = self.get_object()

        # Verificar permisos del usuario
        if not es_usuario_autorizado_para_sector(request, formulario_sectorial):
            return Response({"detail": "No autorizado para editar este documento."},
                            status=status.HTTP_403_FORBIDDEN)

        flujograma_competencia_id = request.data.get('flujograma_competencia_id')
        documento_file = request.FILES.get('documento')  # Esta es la línea que extrae el archivo del request

        if not documento_file:
            return Response({"error": "Documento es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        if flujograma_competencia_id:
            # Intenta actualizar un FlujogramaCompetencia existente
            try:
                flujograma_competencia = FlujogramaCompetencia.objects.get(id=flujograma_competencia_id, formulario_sectorial=formulario_sectorial)
            except FlujogramaCompetencia.DoesNotExist:
                return Response({"error": "FlujogramaCompetencia no encontrado."}, status=status.HTTP_404_NOT_FOUND)
            
            flujograma_competencia.flujograma_competencia = documento_file  # Asegúrate de usar el campo correcto aquí
            flujograma_competencia.save()

            return Response({"mensaje": "Documento actualizado con éxito."})
        else:
            # Crea un nuevo FlujogramaCompetencia si no se proporciona ID
            flujograma_competencia = FlujogramaCompetencia.objects.create(
                formulario_sectorial=formulario_sectorial,
                flujograma_competencia=documento_file  # Asegúrate de usar el campo correcto aquí también
            )

            return Response({"mensaje": "Documento creado con éxito.", "flujograma_competencia_id": flujograma_competencia.id},
                            status=status.HTTP_201_CREATED)


    @action(detail=True, methods=['patch'], url_path='update-organigrama-regional',
            parser_classes=(MultiPartParser, FormParser))
    def update_organigrama_regional(self, request, pk=None):
        """
        Un endpoint dedicado para actualizar el documento de un OrganigramaRegional específico.

        Se deben agregar en el body dos keys, organigrama_regional_id: el valor del ID y documento: el archivo a subir.
        Si se proporciona organigrama_regional_id, el endpoint actualiza el documento existente.
        """
        formulario_sectorial = self.get_object()

        # Verificar permisos del usuario
        if not es_usuario_autorizado_para_sector(request, formulario_sectorial):
            return Response({"detail": "No autorizado para editar este documento."},
                            status=status.HTTP_403_FORBIDDEN)

        organigrama_regional_id = request.data.get('organigrama_regional_id')
        documento_file = request.FILES.get('documento')

        if not organigrama_regional_id or not documento_file:
            return Response({"error": "organigrama_regional_id y documento son requeridos."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            organigrama_regional = OrganigramaRegional.objects.get(id=organigrama_regional_id,
                                                                    formulario_sectorial_id=pk)
        except OrganigramaRegional.DoesNotExist:
            return Response({"error": "OrganigramaRegional no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        organigrama_regional.documento = documento_file
        organigrama_regional.save()


class DeleteAntecedenteAdicionalSectorialView(APIView):

    def delete(self, request, pk):
        try:
            formulario = FormularioSectorial.objects.get(pk=pk)
            formulario.delete_file()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FormularioSectorial.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


def descargar_antecedente(request, pk):
    try:
        formulario = FormularioSectorial.objects.get(pk=pk)
        archivo = formulario.antecedente_adicional_sectorial
        if archivo:
            response = HttpResponse(archivo.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{archivo.name}"'
            return response
        raise Http404("No se encontró el archivo.")
    except FormularioSectorial.DoesNotExist:
        raise Http404("No se encontró el formulario correspondiente.")
