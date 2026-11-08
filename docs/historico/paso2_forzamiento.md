# Paso 2 — Forzamiento: marea (FES2022 + TPXO) y atmósfera (ERA5)

Se usan **las dos mareas**: su diferencia es la incertidumbre de la marea de contorno
dentro del conjunto.

## A. ERA5 (Copernicus Climate Data Store) — ~10 min
1. Crear cuenta: https://cds.climate.copernicus.eu (botón *Login/Register*).
2. Entrar al dataset **"ERA5 hourly data on single levels from 1940 to present"**, pestaña
   *Download*, bajar al final y **aceptar la licencia** (sin esto la API da error).
3. En tu perfil copiar el **Personal Access Token**.
4. En el Mac, en Terminal:
   ```bash
   cat > ~/.cdsapirc <<'X'
   url: https://cds.climate.copernicus.eu/api
   key: PEGA-AQUI-TU-TOKEN
   X
   chmod 600 ~/.cdsapirc
   ```
   (El token no se pega en el chat.)

## B. FES2022 (AVISO+) — alta en minutos, aprobación puede tardar días
1. Formulario: https://www.aviso.altimetry.fr/en/data/data-access/registration-form.html
2. En *Auxiliary Products* marcar **"FES (Finite Element Solution - Oceanic Tides Heights)"**.
   Uso: investigación académica, ULB.
3. Llegan dos correos (registro + credenciales). Guardar usuario y contraseña; no pegarlos en el chat.

## C. TPXO10-atlas (Oregon State) — por correo, gratis para uso académico
Enviar a Svetlana.Erofeeva@oregonstate.edu (copia a Gary.Egbert@oregonstate.edu):

> Subject: TPXO10-atlas-v2 request for academic research
>
> Dear Dr. Erofeeva,
> I am a PhD researcher at the Université libre de Bruxelles (Belgium) working on an
> ensemble hydrodynamic model of Havana Bay, Cuba (residence time and pollutant fate).
> I would like to request access to **TPXO10-atlas-v2 in NetCDF format** for
> non-commercial academic research, to force the open boundary of the model and to
> compare it with FES2022.
> Best regards,
> Alex Manuel Rivera — Université libre de Bruxelles

## Cuando tengas A (y B o C)
Avisar. Se preparan los scripts de descarga (se ejecutan en tu Terminal):
- ERA5, dominio 22,8–23,5 N / 82,8–81,9 W, horario, 2016–2025 (igual que Sentinel-2):
  viento a 10 m, presión a nivel del mar, temperatura y punto de rocío a 2 m,
  radiación solar y térmica, precipitación (lo necesario para el 3D).
- Armónicos de marea en la frontera exterior del modelo, y en la bocana para
  actualizar el prisma (`scripts/prisma_marea.py`).
