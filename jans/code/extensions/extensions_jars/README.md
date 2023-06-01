
**bootsfaces-1.6.0-SNAPSHOT-jakarta.jar**

**bootsfaces** versions: **1.5.0**, **1.4.x** don't support **jakarta**.

**bootsfaces** versions: **1.6.X** support **jakarta**:

```xml
		<dependency>
			<groupId>net.bootsfaces</groupId>
			<artifactId>bootsfaces</artifactId>
			<version>1.6.0-SNAPSHOT</version>
			<classifier>jakarta</classifier>
		</dependency>
```

.

**bootsfaces** version: **1.6.0** isn't released yet (for example: **1.6.0-SNAPSHOT**). Should be used till **bootsfaces** version: **1.6.0** isn't released.

Build:

* **git clone https://github.com/TheCoder4eu/BootsFaces-OSP.git**;

* **cd BootsFaces-OSP**;

* **mvn clean package** or **mvn clean install**;

* result file: **BootsFaces-OSP/target/bootsfaces-1.6.0-SNAPSHOT-jakarta.jar**;

* copy built jar (**bootsfaces-1.6.0-SNAPSHOT-jakarta.jar**) to the directory: **/opt/jans/jetty/jans-auth/custom/libs**;

* open file: **/opt/jans/jetty/jans-auth/webapps/jans-auth.xml**;

* add extension lib: **./custom/libs/bootsfaces-1.6.0-SNAPSHOT-jakarta.jar**:

	```text
	<Set name="extraClasspath">./custom/libs/twilio-7.17.0.jar,./custom/libs/jsmpp-2.3.7.jar,./custom/libs/ztrust-ext-4.4.2.Final.jar,./custom/libs/bootsfaces-1.6.0-SNAPSHOT-jakarta.jar</Set></Configure>
	```

* restart jans-auth:

	```bash
	service jans-auth restart  
	```
	.