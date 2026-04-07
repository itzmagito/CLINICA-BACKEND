import os
import glob
import xml.etree.ElementTree as ET

base_path = "ClinicaPrivadaWS/src/main/java/pe/edu/pucp"
files = glob.glob(f"{base_path}/**/*WS.java", recursive=True)

endpoints = []
for filepath in files:
    filename = os.path.basename(filepath)
    class_name = filename.replace('.java', '')
    
    # Calculate fully qualified class name
    rel_path = os.path.relpath(filepath, "ClinicaPrivadaWS/src/main/java")
    fqcn = rel_path.replace(os.sep, '.').replace('.java', '')
    
    endpoints.append((class_name, fqcn))

# 1. Generate sun-jaxws.xml
sun_jaxws = '<?xml version="1.0" encoding="UTF-8"?>\n<endpoints xmlns="http://java.sun.com/xml/ns/jax-ws/ri/runtime" version="2.0">\n'
for name, fqcn in endpoints:
    sun_jaxws += f'  <endpoint name="{name}" implementation="{fqcn}" url-pattern="/{name}"/>\n'
sun_jaxws += '</endpoints>\n'

with open("ClinicaPrivadaWS/src/main/webapp/WEB-INF/sun-jaxws.xml", "w", encoding="utf-8") as f:
    f.write(sun_jaxws)

print("Created sun-jaxws.xml")

# 2. Modify web.xml
web_xml_path = "ClinicaPrivadaWS/src/main/webapp/WEB-INF/web.xml"
with open(web_xml_path, "r", encoding="utf-8") as f:
    web_xml = f.read()

if "WSServletContextListener" not in web_xml:
    listener_str = """
    <listener>
        <listener-class>com.sun.xml.ws.transport.http.servlet.WSServletContextListener</listener-class>
    </listener>
    <servlet>
        <servlet-name>JAXWSServlet</servlet-name>
        <servlet-class>com.sun.xml.ws.transport.http.servlet.WSServlet</servlet-class>
        <load-on-startup>1</load-on-startup>
    </servlet>
"""
    for name, _ in endpoints:
        listener_str += f"""    <servlet-mapping>
        <servlet-name>JAXWSServlet</servlet-name>
        <url-pattern>/{name}</url-pattern>
    </servlet-mapping>\n"""

    web_xml = web_xml.replace("<servlet>", listener_str + "\n\t<servlet>", 1)
    
    with open(web_xml_path, "w", encoding="utf-8") as f:
        f.write(web_xml)
    print("Modified web.xml to include WSServlet")

# 3. Modify pom.xml
pom_path = "ClinicaPrivadaWS/pom.xml"
with open(pom_path, "r", encoding="utf-8") as f:
    pom_xml = f.read()

# removing <scope>provided</scope> for webservices-rt to package it into the WAR
old_dep = """        <dependency>
            <groupId>org.glassfish.metro</groupId>
            <artifactId>webservices-rt</artifactId>
            <version>2.3</version>
            <scope>provided</scope>
        </dependency>"""

new_dep = """        <dependency>
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

if old_dep in pom_xml:
    pom_xml = pom_xml.replace(old_dep, new_dep)
    with open(pom_path, "w", encoding="utf-8") as f:
        f.write(pom_xml)
    print("Modified pom.xml to bundle webservices-rt")

# 4. Revert Dockerfile
dockerfile_path = "Dockerfile"
with open(dockerfile_path, "r", encoding="utf-8") as f:
    dockerfile = f.read()
dockerfile = dockerfile.replace("payara/server-full:6.2025.5-jdk21", "payara/micro:6.2025.5-jdk21")
with open(dockerfile_path, "w", encoding="utf-8") as f:
    f.write(dockerfile)
print("Reverted Dockerfile")

