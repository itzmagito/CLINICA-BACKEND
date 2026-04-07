# Etapa 1: Compilar la aplicacion con Maven
FROM maven:3.9.6-eclipse-temurin-21 AS build
WORKDIR /app

# Copiar el root pom y el codigo fuente
COPY pom.xml .
COPY ClinicaPrivada/ ClinicaPrivada/
COPY ClinicaPrivadaBusiness/ ClinicaPrivadaBusiness/
COPY ClinicaPrivadaDBManager/ ClinicaPrivadaDBManager/
COPY ClinicaPrivadaDomain/ ClinicaPrivadaDomain/
COPY ClinicaPrivadaPersistance/ ClinicaPrivadaPersistance/
COPY ClinicaPrivadaWS/ ClinicaPrivadaWS/

# Ejecutar el build saltandose los tests
RUN mvn clean package -DskipTests

# Etapa 2: Ejecutar en WildFly (Servidor Jakarta EE ligero y rapido)
FROM quay.io/wildfly/wildfly:latest-jdk21

# Copiar el WAR compilado a la carpeta de despliegue
COPY --from=build /app/ClinicaPrivadaWS/target/ClinicaPrivadaWS-1.0-SNAPSHOT.war /opt/jboss/wildfly/standalone/deployments/ClinicaPrivadaWS.war

# WildFly hace un escaneo automatico y publica WebServices
EXPOSE 8080
CMD ["/opt/jboss/wildfly/bin/standalone.sh", "-b", "0.0.0.0"]
