import os

# 1. Restore pom.xml to use scope=provided for Metro -> Let WildFly handle JAX-WS natively
pom_path = "ClinicaPrivadaWS/pom.xml"
with open(pom_path, "r", encoding="utf-8") as f:
    pom_xml = f.read()

old_dep = """        <dependency>
            <groupId>org.glassfish.metro</groupId>
            <artifactId>webservices-rt</artifactId>
            <version>2.3</version>
        </dependency>
        <!-- Need activation explicitly sometimes for Metro 2.3 -->
        <dependency>
            <groupId>jakarta.activation</groupId>
            <artifactId>jakarta.activation-api</artifactId>
            <version>2.1.2</version>
        </dependency>"""

new_dep = """        <dependency>
            <groupId>org.glassfish.metro</groupId>
            <artifactId>webservices-rt</artifactId>
            <version>2.3</version>
            <scope>provided</scope>
        </dependency>"""

if old_dep in pom_xml:
    pom_xml = pom_xml.replace(old_dep, new_dep)
    with open(pom_path, "w", encoding="utf-8") as f:
        f.write(pom_xml)
    print("Restored pom.xml")

# 2. Remove sun-jaxws.xml
sun_jaxws = "ClinicaPrivadaWS/src/main/webapp/WEB-INF/sun-jaxws.xml"
if os.path.exists(sun_jaxws):
    os.remove(sun_jaxws)
    print("Removed sun-jaxws.xml")

# 3. Clean web.xml
web_xml_path = "ClinicaPrivadaWS/src/main/webapp/WEB-INF/web.xml"
with open(web_xml_path, "r", encoding="utf-8") as f:
    web_xml = f.read()

# We just rewrite it from scratch because it's tiny
simple_web_xml = """<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee"
   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee https://jakarta.ee/xml/ns/jakartaee/web-app_6_0.xsd"
   version="6.0">
    <session-config>
        <session-timeout>
            30
        </session-timeout>
    </session-config>
	<servlet>
        <servlet-name>ReporteCitasXPaciente</servlet-name>
        <servlet-class>pe.edu.pucp.servlets.ReporteCitasXPaciente</servlet-class>
    </servlet>

    <servlet-mapping>
        <servlet-name>ReporteCitasXPaciente</servlet-name>
        <url-pattern>/ReporteCitasXPaciente</url-pattern>
    </servlet-mapping>
	
	<servlet>
		<servlet-name>ReporteAtencionXMedico</servlet-name>
		<servlet-class>pe.edu.pucp.servlets.ReporteAtencionXMedico</servlet-class>
	</servlet>

	<servlet-mapping>
		<servlet-name>ReporteAtencionXMedico</servlet-name>
		<url-pattern>/ReporteAtencionXMedico</url-pattern>
	</servlet-mapping>

</web-app>"""

with open(web_xml_path, "w", encoding="utf-8") as f:
    f.write(simple_web_xml)
print("Cleaned web.xml")


# 4. Modify Dockerfile to use WildFly
dockerfile = """# Etapa 1: Compilar la aplicacion con Maven
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
FROM quay.io/wildfly/wildfly:31.0.1.Final-jdk21

# Copiar el WAR compilado a la carpeta de despliegue
COPY --from=build /app/ClinicaPrivadaWS/target/ClinicaPrivadaWS-1.0-SNAPSHOT.war /opt/jboss/wildfly/standalone/deployments/ClinicaPrivadaWS.war

# WildFly hace un escaneo automatico y publica WebServices
EXPOSE 8080
CMD ["/opt/jboss/wildfly/bin/standalone.sh", "-b", "0.0.0.0"]
"""
dockerfile_path = "Dockerfile"
with open(dockerfile_path, "w", encoding="utf-8") as f:
    f.write(dockerfile)
print("Updated Dockerfile for WildFly")

