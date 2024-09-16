from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import CharMap
from .serializer import CharSerializer

@api_view(['GET'])
def get_all_chars(request):
    #get all objects
    allChars = CharMap.objects.all()
    #convert to json
    serializedData = CharSerializer(allChars, many=True).data
    return Response(serializedData)

@api_view(['POST'])
def create_char(request):
    #get data from front end
    data = request.data
    serializer = CharSerializer(data = data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT','DELETE'])
def char_detail(request, pk):
    try :
        char = CharMap.objects.get(pk=pk)
    except CharMap.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        char.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    elif request.method == 'PUT':
        data = request.data
        serializer = CharSerializer(char, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    

