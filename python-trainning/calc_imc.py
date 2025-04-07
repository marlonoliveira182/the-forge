name = 'Marlon Oliveira'
height = 1.72
weight = 104.0
imc = weight / (height ** 2)

if imc < 18.5:
    result = 'Magreza'
elif 18.5 <= imc <= 24.9:
    result = 'Peso normal'
elif 25 <= imc <= 29.9:
    result = 'Sobrepeso'
elif 30 <= imc <= 34.9:
    result = 'Obesidade grau I'
elif 35 <= imc <= 39.9:
    result = 'Obesidade grau II'
elif 40 <= imc:
    result = 'Obesidade grau III'

print('Seu IMC é: ' + str(imc) + ', ' +  result)
    
     

