1. Broken Authentication: conocemos el usuario empresarial de Carlos, `carlos@mi_empresa.com`.
Probamos con una lista de contraseñas conocidas y encontramos que la contraseña es `password1234`
   
2. Una vez adentro, vamos al Perfil. Allí se ve una foto de perfil del usuario.
Abriendo la foto para verla en tamaño completo, se ve que el URL es `http://localhost:5000/images?image_name=static%2Fprofile_picture.png`.
   Cambiando el query param `image_name` a `config.json` se puede realizar un directory traversal.
   Dentro del archivo `config.json` se ve un usuario y contraseña de administrador que se crea la primera vez que se levanta el server.
   Se prueba utilizarlas para iniciar sesión y efectivamente funcionan.
   
3. Una vez loggeado como administrador, tenemos acceso al form de creación de Noticias.
Se prueba hacer un XSS directo en ese Form, pero la página que muestra las noticias 
   tiene los datos sanitizados. Sin embargo sí, se puede realizar un SQL Injection.
   
4. El SQL Injection que realizamos es el siguiente:
``');update title set text="
<script>
alert('Felicitaciones! Como festejo del día de la primavera,
la wiki empresarial está devolviendo los favores a sus empleados.
Deposite aquí cualquier cantidad de bitcoins y se le devolverá el doble:
wallet-56712345987')
</script>
" where id=1;--``. Luego vamos a la pestaña Home y vemos
   que se ejecuta el alert().