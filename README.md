# GIROS CI/CD Demo

El objetivo de este repositorio es demostrar cómo se pueden aprovechar las capacidades y herramientas
que proporciona GitHub para automatizar tareas siguiendo las prácticas CI/CD (Integración continua/despliegue continuo). En concreto:

- Cómo construir una imagen Docker de manera automática cada vez que creamos una `Release`.
- Cómo empaquetar y publicar un Helm chart de Kubernetes de manera automática, también cada vez que creamos una `Release`.

Para este repositorio definimos como proyecto de ejemplo el desarrollo de un microservicio con una API REST con un único método GET disponible. Al llamar a la API, nos devuelve una respuesta que sigue el siguiente esquema JSON:

```json
{
    "who": "String, dirección IP de quien hace la llamada.",
    "where": "Integer, puerto usado por quien hace la llamada.",
    "when": "String, timestamp de la recepción de la llamada.",
    "message": "Hello"
}
```

La API REST está implementada con [FastAPI](https://fastapi.tiangolo.com/), usando [Uvicorn](https://www.uvicorn.org/) como servidor Web y [Pydantic](https://docs.pydantic.dev/latest/) para la definición del esquema/modelo de la respuesta. El código fuente está [aquí](ci_cd_demo/main.py).

## Flujos de trabajo

Los flujos de trabajo definen un conjunto de pasos que son ejecutados dentro del contexto de las ([GitHub Actions](https://github.com/features/actions)).

En [este directorio](.github/workflows/) se encuentran dos ficheros YAML que definen los flujos de trabajo de GitHub que permiten:

1) Compilar y publicar la imagen Docker como paquete en el repositorio: [docker-build-and-push.yaml](.github/workflows/docker-build-and-push.yaml).
2) Empaquetar y publicar el Helm chart en las GitHub Pages del repositorio para poder desplegar la app en Kubernetes: [package-and-publish-helm-chart.yaml](.github/workflows/package-and-publish-helm-chart.yaml).

Como requisito previo, es necesario configurar el repositorio que vayamos a utilizar para que las GitHub Actions tengan permisos de lectura y escritura. También, definiremos las siguientes ramas:
- `main` como rama principal, para código estable y probado.
- `develop` como rama **por defecto**, donde subiremos el código en desarrollo.

Lo ideal sería que el repositorio fuese público. En caso de ser privado, el workflow 1 funcionaría, aunque será necesario identificarse a la hora de descargar la imagen Docker. El workflow 2 con cuentas gratuitas de GitHub requiere que el repositorio sea público.

La manera óptima de trabajar sería subir cambios en el código y en el contenido del repositorio a la rama `develop`. Una vez completados esos cambios (por ejemplo, porque ya tenemos una versión estable y probada del código), se hace una `Pull Request` a la rama `main` desde `develop`. Cuando se haga el `merge`, crearíamos una `Release` tomando la rama `main` como base y definiendo una etiqueta/`tag` con el número de versión (por ejemplo, `1.0.0`). Si se va a trabajar en una característica muy concreta, crear una nueva rama tomando `develop` como base y, al completar el desarrollo, hacer una `Pull Request` desde esa rama a `develop`.

Los ficheros YAML sirven como plantillas para otros casos, así que se pueden tomar como base y editar según corresponda.

### Flujo 1 - Compilar y publicar la imagen Docker como paquete en el repositorio

GitHub nos proporciona un registro de imágenes Docker a través de los GitHub Packages. Este workflow automatiza los siguientes pasos cuando creamos una `Release` en el repositorio que toma como rama base la rama `main`:

1) Compila la imagen Docker y la etiqueta como `latest`.
2) Publica esa imagen Docker en GitHub Packages.
3) Crea una etiqueta para la imagen Docker con el número de versión definido en la `tag` de la `Release`.
4) Publica la imagen Docker con la etiqueta que contiene el número de versión en GitHub Packages.

Una vez publicada, la imagen Docker estará disponible en:

```
ghcr.io/<nuestro_nombre_de_usuario_o_de_organización>/<nombre_del_repositorio>:latest

ghcr.io/<nuestro_nombre_de_usuario_u_organización>/<nombre_del_repositorio>:<número_de_versión>
```

Para este repositorio concreto, la imagen estará disponible en:

```
ghcr.io/giros-dit/ci-cd-demo:latest

ghcr.io/giros-dit/ci-cd-demo:1.0.0
```

#### Instrucciones completas

1) Crear el directorio `.github/workflows` en el repositorio y subir ahí la plantilla [`docker-build-and-push.yaml`](.github/workflows/docker-build-and-push.yaml).
2) Realizar todas las operaciones de `push` que sean necesarias a la rama `develop` (rama por defecto para trabajar).
3) Una vez actualizado el repositorio en `develop`, crear una `Pull request` para hacer _merge_ de `develop` en `main`.
4) Con la `Pull request` completada, verificar que la rama `main` está actualizada y, a continuación, crear una `Release`. Para ello, en el repositorio, hay que dirigirse a `Releases` (ubicado en la parte derecha) y, después, pulsar en `Draft a new release`. En `Choose a new tag` se introduce el número de versión (por ejemplo, `1.0.0`) y se pulsa en `+ Create new tag: <versión> on publish`. Después, se da un título y una descripción a la `Release`. Una vez completado, en la parte de abajo, se marca la opción `Set as the latest release` si ya había una `Release` previa y se pulsa sobre `Publish release`.
5) Con la `Release` publicada, se lanzará el flujo de trabajo. Se puede comprobar su ejecución en el menú `Actions` del repositorio. Debería completarse sin problemas. Una vez completado, se comprueba que se ha subido el `Package` correspondiente en la sección `Packages` ubicado en la parte derecha de la vista del repositorio, bajo `Releases`.
6) Finalmente, comprobar que el `Package` que se ha subido está etiquetado con la misma versión que la `Release` además de `latest`, así como que la visibilidad está establecida en `Public` (esto último se puede comprobar en `Package settings` --> `Danger zone` -> `Change package visibility`).

### Flujo 2 - Empaquetar y publicar el Helm chart en las GitHub Pages del repositorio para poder desplegar la app en Kubernetes

En este caso, aprovecharemos las GitHub Pages para tener un repositorio Helm asociado a nuestro repositorio de GitHub. Respecto a esto, podemos identificar varias maneras de trabajar:

1) El desarrollo del Helm chart se realiza en el mismo repositorio de GitHub que usamos para el desarrollo del código de nuestra aplicación/servicio. La publicación se hace en las GitHub Pages del mismo repositorio. **ESTE EJEMPLO**.

2) El desarrollo del Helm chart se realiza en un repositorio aparte, también en GitHub. Por ejemplo, si nuestro repositorio para la aplicación se llama `demo`, el repositorio para el Helm chart se llamaría `demo-helm`. La publicación del chart se realiza en las GitHub Pages de este último repositorio.

3) Podemos tener un repositorio en GitHub para desarrollar múltiples Helm charts. En este caso, centralizamos el desarrollo en un único repositorio de nombre, por ejemplo, `helm-charts`. Los charts se publicarían en las GitHub Pages de ese repositorio, donde se publicarían todos los charts de todas las aplicaciones que desarrollemos.

Este workflow automatiza los siguientes pasos cuando creamos una `Release` en el repositorio que toma como rama base la rama `main`:

1) Empaqueta el Helm chart y lo mueve a un directorio en el contexto del workflow llamado `/packages`.
2) Se crea el índice del repositorio Helm con el contenido del directorio `/packages` y se construye la URL desde la que se podrá acceder a él.
3) Se publica el repositorio Helm a las GitHub Pages.

**IMPORTANTE**: El primer despliegue en las GitHub Pages tiene algunas limitaciones ([ver referencia](https://github.com/peaceiris/actions-gh-pages#%EF%B8%8F-first-deployment-with-github_token)) que es necesario resolver de forma manual (__solo la primera vez__). El flujo de trabajo crea una rama en el repositorio, de nombre `gh-pages`, que hay que configurar como fuente para que la compilación y el despliegue de `GitHub Pages` se hagan desde esta rama. Para ello, en `Settings` --> `Code and automation` -> `Pages`, en la sección `Build and deployment`, es necesario marcar la opción `Deploy from a branch` en `Source` y seleccionar la rama `gh-pages` en el desplegable bajo `Branch`. Finalmente, pulsar el botón `Save` para guardar los cambios. El despliegue debería completarse sin realizar ninguna acción más.

En este caso concreto, que se corresponde con la manera de trabajar **1** desarrollada antes, el repositorio Helm estará disponible en la siguiente URL:

```
https://<nuestro_nombre_de_usuario_u_organización>.github.io/<nombre_del_repositorio>/
```

Tomando los valores concretos del repositorio:

```
https://giros-dit.github.io/ci-cd-demo/
```

Para instalar el Helm chart, ejecutaríamos:

```shell
$ helm repo add ci-cd-demo https://giros-dit.github.io/ci-cd-demo/
$ helm repo update ci-cd-demo
$ helm install ci-cd-demo ci-cd-demo/ci-cd-demo
```

Y para desinstalar:

```shell
$ helm uninstall ci-cd-demo
```

#### Instrucciones completas

1) Crear el directorio `.github/workflows` en el repositorio y subir ahí la plantilla [`package-and-publish-helm-chart.yaml`](.github/workflows/package-and-publish-helm-chart.yaml).
2) Crear el Helm chart y subirlo al repositorio.
3) Realizar todas las operaciones de `push` que sean necesarias a la rama `develop` (rama por defecto para trabajar).
4) Una vez actualizado el repositorio en `develop`, crear una `Pull request` para hacer _merge_ de `develop` en `main`.
5) Con la `Pull request` completada, verificar que la rama `main` está actualizada y, a continuación, crear una `Release`. Para ello, en el repositorio, hay que dirigirse a `Releases` (ubicado en la parte derecha) y, después, pulsar en `Draft a new release`. En `Choose a new tag` se introduce el número de versión (por ejemplo, `1.0.0`) y se pulsa en `+ Create new tag: <versión> on publish`. Después, se da un título y una descripción a la `Release`. Una vez completado, en la parte de abajo, se marca la opción `Set as the latest release` si ya había una `Release` previa y se pulsa sobre `Publish release`.
6) Con la `Release` publicada, se lanzará el flujo de trabajo. Se puede comprobar su ejecución en el menú `Actions` del repositorio.
7) El primer despliegue tiene algunas limitaciones ([ver referencia](https://github.com/peaceiris/actions-gh-pages#%EF%B8%8F-first-deployment-with-github_token)) que es necesario resolver de forma manual (__solo la primera vez__). El flujo de trabajo crea una rama en el repositorio, de nombre `gh-pages`, que hay que configurar como fuente para que la compilación y el despliegue de `GitHub Pages` se hagan desde esta rama. Para ello, en `Settings` --> `Code and automation` -> `Pages`, en la sección `Build and deployment`, es necesario marcar la opción `Deploy from a branch` en `Source` y seleccionar la rama `gh-pages` en el desplegable bajo `Branch`. Finalmente, pulsar el botón `Save` para guardar los cambios. El despliegue debería completarse sin realizar ninguna acción más.
8) La URL de `GitHub Pages` será `https://giros-dit.github.io/<nombre-del-repositorio>/`. Esta URL es la misma donde se encuentra disponible el repositorio Helm y que puede utilizarse para instalar el chart correspondiente:

```shell
$ helm repo add <nombre-del-repositorio> https://giros-dit.github.io/<nombre-del-repositorio>/
$ helm install <nombre-del-chart> <nombre-del-repositorio>/<nombre-del-chart>
```

**Nota adicional 1**: Si se visita la URL de `GitHub Pages` desde un navegador Web, se obtendrá un error `404 Not Found`. Esto se debe a que el _job_ de la acción que realiza el despliegue no sube un fichero `README.md` a modo de página índice. Esto puede solucionarse creando dicho fichero y editando la plantilla del flujo de trabajo para que lo despliegue.

**Nota adicional 2**: Respecto al control de versiones, se sospecha que no es posible tener varias versiones de un Helm chart utilizando este método de `GitHub Pages`, ya que cada nueva `Release` que se publique en el repositorio las compila desde cero.
