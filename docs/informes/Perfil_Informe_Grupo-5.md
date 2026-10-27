**Plataforma Web y Aplicación Móvil para la Trazabilidad de Dispositivos Apple mediante Tecnología Blockchain, desde el Origen hasta el Consumidor Final** 

# **1\. INTRODUCCIÓN**

En el comercio electrónico actual, el consumidor ha pasado de ser un receptor pasivo de productos a un agente activo que exige transparencia, autenticidad y responsabilidad social en cada compra. Esta exigencia se ha intensificado en sectores como la electrónica de consumo, donde el valor del producto, la sofisticación tecnológica y el riesgo de adquisición de dispositivos falsificados o de procedencia ilícita convierten a la confianza en un activo crítico para la decisión de compra. En Bolivia, el mercado de dispositivos Apple —iPhones, MacBooks, iPads y accesorios— ha experimentado un crecimiento sostenido en los últimos años, impulsado por una demanda creciente de productos de alta gama que no son fabricados en la región y que dependen completamente de cadenas de importación desde Estados Unidos. Sin embargo, la mayoría de los sistemas de información empresarial disponibles en el país no ofrecen una visibilidad completa del ciclo de vida de estos productos, limitándose a registrar fragmentos de información que no son verificables por el consumidor final, lo que genera desconfianza, incertidumbre y una exposición significativa al fraude y a la comercialización de productos no originales.

La tecnología blockchain ha demostrado ser una solución idónea para este desafío. Su naturaleza descentralizada, inmutable y transparente permite registrar cada etapa de la cadena de suministro —desde la compra en el proveedor estadounidense, pasando por el transporte internacional, el despacho aduanero en Bolivia, el almacenamiento, la distribución y la venta al consumidor— sin que ningún actor pueda alterar los datos retrospectivamente. Al combinar esta tecnología con códigos QR únicos asignados a cada dispositivo según su número de serie, IMEI o EID, el producto se convierte en un portador de su propia historia digital: el consumidor puede escanear el código desde su teléfono y acceder a un registro verificable del origen, las condiciones de transporte, los procesos de importación, la autenticidad y el historial completo del dispositivo adquirido.

El presente documento expone el perfil del proyecto Sistema de Información Empresarial para Plataforma y Aplicación Móvil con Blockchain para la Trazabilidad de Dispositivos Apple Importados, un sistema web y móvil desarrollado para empresas bolivianas importadoras, distribuidoras y tiendas de productos electrónicos que desean incorporar trazabilidad blockchain como un atributo diferenciador en el comercio electrónico, ofreciendo a sus clientes la certeza de estar adquiriendo un dispositivo genuino, con un historial verificable y condiciones de transporte documentadas.

El sistema permitirá que los importadores registren las órdenes de compra en Estados Unidos, documenten el transporte internacional (con monitoreo de condiciones como temperatura, humedad y vibración), gestionen la recepción en aduanas y almacenes, y asignen a cada unidad un código QR único vinculado a su número de serie. Los distribuidores y tiendas podrán registrar los traslados logísticos y las ventas, mientras que el consumidor, desde la aplicación móvil o la tienda online, podrá escanear el código del dispositivo para conocer todo su historial, desde la compra original hasta el momento de la venta. La plataforma incorpora cuatro elementos clave: la inmutabilidad de los registros mediante blockchain, la verificación de autenticidad y origen, la generación automática de certificados digitales de trazabilidad y la integración con el carrito de compra para visualizar el historial de los productos seleccionados.

El documento se organiza en doce secciones. Tras esta introducción, la sección de antecedentes presenta la fundamentación teórica de la trazabilidad blockchain, los sistemas similares existentes en el mercado internacional y los casos de estudio seleccionados para su análisis detallado. A continuación, se plantea la descripción del problema que motiva el desarrollo, se definen los objetivos generales y específicos, y se delimita el alcance del sistema. Las secciones siguientes describen los elementos del sistema de información basado en computadoras (SIBC), las tecnologías seleccionadas para el desarrollo y la puesta en marcha, los costos estimados de implementación y los beneficios esperados para el cliente.

# **2\. ANTECEDENTES**

La preocupación del consumidor por el origen, la autenticidad y la calidad de los productos que adquiere no es un fenómeno reciente, pero la tecnología ha modificado radicalmente la forma de satisfacer esa demanda. Durante décadas, la trazabilidad de los productos fue un proceso interno de las empresas —registros en papel, planillas de control y bases de datos internas— que raramente llegaba al consumidor final. En el sector de la electrónica de consumo, esta limitación era particularmente crítica, ya que los dispositivos de alta gama como los fabricados por Apple son objetivos frecuentes de falsificación, robo y comercialización ilegal. La información sobre el origen, la fecha de compra, las condiciones de transporte y la autenticidad se limitaba a la etiqueta impresa en la caja, sin posibilidad de verificación externa más allá de la consulta del número de serie en el sitio web del fabricante, que solo confirma la garantía del equipo pero no documenta su recorrido logístico ni su historial de propiedad.

La aparición de los códigos de barras y, posteriormente, de los códigos QR permitió digitalizar parte de esa información y hacerla accesible desde el teléfono del consumidor. Sin embargo, estos sistemas presentaban un problema fundamental: la información contenida en esos códigos podía ser falsificada o modificada sin dejar rastro, lo que limitaba su utilidad como mecanismo de confianza. La credibilidad de la trazabilidad dependía, en última instancia, de la honestidad del importador o del vendedor, no de la robustez del sistema. Para un dispositivo Apple, esta vulnerabilidad es especialmente grave, ya que la diferencia entre un iPhone genuino y una réplica de alta calidad puede ser casi imperceptible para el consumidor no experto, pero representa una pérdida económica significativa y un riesgo para la seguridad de los datos personales.

La evolución de la trazabilidad adquirió un nuevo rumbo con la maduración de la tecnología blockchain. Almacenar los registros de la cadena de suministro en un libro de contabilidad distribuido e inmutable resuelve el problema de la falsificación retrospectiva: una vez que un evento queda registrado en la blockchain —como la compra en el proveedor estadounidense, el embarque en el puerto de origen, el despacho aduanero en Bolivia, la recepción en el almacén o la venta al consumidor— ningún actor puede modificarlo sin que el resto de la red lo detecte. Esta característica convierte a la blockchain en el soporte tecnológico idóneo para la trazabilidad de dispositivos electrónicos importados, ya que el consumidor puede confiar en que la información que lee es la misma que se registró en el momento en que ocurrió cada evento, garantizando la autenticidad del equipo desde su origen en Estados Unidos.

En el contexto del comercio electrónico boliviano, esta tecnología adquiere un valor estratégico adicional. La distancia física entre el vendedor y el comprador, sumada a la complejidad de los procesos de importación —que involucran transporte internacional, despacho aduanero, almacenamiento y distribución— hace que la confianza sea un activo crítico. El consumidor que compra un iPhone online no puede tocar el dispositivo ni inspeccionarlo antes de pagar; depende completamente de la reputación del vendedor y de la información proporcionada. Un sistema de trazabilidad blockchain que le permita verificar el origen, la autenticidad y el historial completo del dispositivo —incluyendo las condiciones de transporte (temperatura, humedad, vibración), los actores intervinientes y las fechas de cada evento— reduce significativamente la incertidumbre de la compra remota y puede convertirse en un factor determinante de la decisión de compra, especialmente en un mercado donde los dispositivos Apple representan una inversión considerable para el consumidor promedio.

El análisis de las plataformas comerciales e institucionales existentes constituye, por tanto, un referente fundamental para el desarrollo del sistema propuesto, ya que permite identificar las funcionalidades consolidadas en el mercado, las buenas prácticas de diseño aplicables al contexto boliviano y las capacidades que ninguna de las soluciones disponibles cubre de manera simultánea. Ninguna de las plataformas internacionales de trazabilidad blockchain está diseñada específicamente para el mercado boliviano de importación de productos Apple, ni integra los procesos aduaneros y logísticos locales, lo que valida la oportunidad y la pertinencia del sistema propuesto.

## **2.1. Fundamentación teórica**

El desarrollo de una plataforma de trazabilidad de dispositivos electrónicos importados con blockchain requiere precisar los conceptos que intervienen en la cadena de suministro internacional, las propiedades de la tecnología blockchain y los fundamentos que explican el valor de la trazabilidad para los distintos actores involucrados en el mercado boliviano de productos Apple.

**Trazabilidad de producto**

La trazabilidad se define, según la norma ISO 22005, como la capacidad de seguir el historial, la aplicación o la localización de un producto mediante registros documentados. En la práctica, la trazabilidad implica poder responder, en cada etapa de la cadena de suministro, a las preguntas: ¿de dónde viene este producto?, ¿qué se le ha hecho y por quién?, ¿y a dónde ha ido después? Una trazabilidad completa abarca desde el origen de la materia prima —la "cuna"— hasta el consumidor final —la "tumba" o "mesa"— y se denomina trazabilidad de extremo a extremo. Para el caso de dispositivos Apple importados, esta trazabilidad debe iniciar en el proveedor estadounidense (Apple Inc. o distribuidores autorizados), atravesar el transporte internacional, el despacho aduanero en Bolivia, el almacenamiento y la distribución, y culminar en la venta al consumidor final, documentando cada evento con la identificación única del dispositivo mediante su número de serie, IMEI o EID.

**Cadena de suministro**

La cadena de suministro es el conjunto de actores, actividades, recursos y tecnologías involucrados en la creación y entrega de un producto, desde la obtención de la materia prima hasta la entrega al consumidor. Comprende a los proveedores de insumos, los productores, los procesadores, los distribuidores, los minoristas y, finalmente, el consumidor. Cada eslabón de la cadena genera información que, en una trazabilidad completa, debe registrarse y vincularse al lote o unidad de producto correspondiente.

En el contexto de la importación de dispositivos Apple a Bolivia, la cadena de suministro presenta características particulares: los proveedores se ubican en Estados Unidos (Apple Inc., distribuidores mayoristas como Ingram Micro o TD Synnex, o tiendas como Best Buy), los transportistas internacionales gestionan el envío marítimo o aéreo, las aduanas bolivianas intervienen en el despacho de importación, los almacenes y centros de distribución reciben y consolidan la mercancía, y finalmente las tiendas físicas y canales de comercio electrónico realizan la venta al consumidor. Cada uno de estos eslabones debe quedar documentado en el sistema de trazabilidad.

**Tecnología blockchain**

Una blockchain (cadena de bloques) es un libro de contabilidad distribuido, inmutable y descentralizado que registra transacciones en bloques encadenados mediante criptografía. Sus propiedades fundamentales, relevantes para la trazabilidad de dispositivos electrónicos importados, son:

* Inmutabilidad: una vez que un registro es confirmado en la blockchain, no puede ser alterado ni eliminado retrospectivamente sin que la red lo detecte. Para un iPhone o MacBook, esto significa que el historial de importación, las condiciones de transporte y la autenticidad del dispositivo quedan fijados de forma permanente, imposibilitando que un vendedor inescrupuloso modifique registros para ocultar un origen ilícito o condiciones de transporte inadecuadas.  
* Transparencia: todos los participantes autorizados —importadores, distribuidores, tiendas y consumidores— pueden consultar los registros de la cadena. El consumidor puede así verificar el origen del dispositivo y cada etapa de su recorrido.  
* Descentralización: no existe un único actor que controle los datos; la confianza se deposita en el protocolo y el consenso de la red. Esta característica es especialmente relevante en un mercado donde la confianza en el importador o el vendedor es el principal activo.  
* Auditabilidad: cada registro queda vinculado a una identidad y a un timestamp, lo que permite reconstruir la secuencia completa de eventos desde la compra en EE.UU. hasta la venta en Bolivia.

**Smart contracts (contratos inteligentes)**

Un contrato inteligente es un programa auto-ejecutable que se almacena en la blockchain y se ejecuta automáticamente cuando se cumplen condiciones predefinidas. En el contexto de la trazabilidad de dispositivos Apple importados, los contratos inteligentes pueden automatizar la verificación de la autenticidad del dispositivo (comparando el número de serie con los registros del fabricante), la generación de certificados digitales de importación, la emisión de certificados de autenticidad para el consumidor, y la generación de alertas cuando se detectan condiciones anómalas en el transporte (temperatura extrema, vibraciones excesivas, retrasos en la cadena logística).

**Identificadores digitales de producto (QR, NFC, RFID)**

Estos dispositivos o códigos constituyen el "puente" físico entre el producto y su registro digital en la blockchain. Para dispositivos Apple, la identificación se complementa con los identificadores únicos del fabricante:

* **Número de serie:** identificador único asignado por Apple a cada dispositivo, que permite consultar el modelo, la capacidad, el color, la fecha de fabricación y la cobertura de garantía.  
* **IMEI (International Mobile Equipment Identity):** número único de 15 dígitos que identifica a cada dispositivo móvil a nivel global, fundamental para la trazabilidad de iPhones y iPads con conectividad celular.  
* **EID (Embedded Identity Document):** identificador para dispositivos con eSIM, que complementa la trazabilidad en equipos modernos.  
* **Código QR:** matriz de puntos que se escanea con la cámara del teléfono y que enlaza a una URL donde se despliega la información del dispositivo. En el sistema propuesto, cada unidad recibe un código QR único generado a partir de su número de serie o IMEI, que el consumidor escanea para acceder a su historial completo.  
* **NFC (Near Field Communication):** etiqueta o chip que se comunica por proximidad con el teléfono, permitiendo una lectura más rápida y segura. Puede implementarse en dispositivos Apple utilizando la tecnología Core NFC disponible en iPhones.  
* **RFID (Radio Frequency Identification):** etiqueta que se lee a distancia mediante ondas de radio, utilizada en la logística y el inventario a gran escala para el seguimiento de pallets y contenedores completos.

**Asimetría de información y señales de calidad**

En el mercado de productos de consumo, el vendedor conoce la calidad y el origen del producto, pero el comprador no puede observarlos directamente antes de la compra. Esta asimetría de información genera desconfianza y puede llevar a un "mercado de limones" (Akerlof, 1970), en el que los productos de baja calidad expulsan a los de alta calidad porque el comprador no puede distinguirlos. En el mercado boliviano de dispositivos Apple, esta asimetría es particularmente pronunciada: el consumidor no puede distinguir un iPhone original importado legalmente de un dispositivo reacondicionado, robado o falsificado, especialmente cuando ambos se comercializan con precios similares. La trazabilidad blockchain actúa como una señal creíble: al exponer el historial completo y verificable del dispositivo —incluyendo su origen, las condiciones de transporte, los procesos aduaneros y la cadena de custodia—, reduce la asimetría de información y permite que los dispositivos genuinos y correctamente importados obtengan una prima en el mercado, al tiempo que desincentiva la comercialización de productos de procedencia ilícita.

**Comercio electrónico y confianza del consumidor**

En el comercio electrónico, la confianza es un factor crítico, ya que el consumidor no puede interactuar físicamente con el producto antes de comprarlo. En Bolivia, donde la compra de un iPhone o MacBook representa una inversión considerable para el consumidor promedio, la incertidumbre es aún mayor. Estudios de mercado han demostrado que los consumidores están dispuestos a pagar más por productos que ofrecen trazabilidad verificable. Un sistema de trazabilidad blockchain integrado al proceso de compra online puede reducir las tasas de abandono del carrito, aumentar la lealtad a la marca y justificar el precio premium que caracteriza a los productos Apple.

**Propuesta de valor para cada actor**

* Para el importador: diferenciación en el mercado, acceso a consumidores dispuestos a pagar una prima por la trazabilidad, reducción del riesgo de fraudes y falsificaciones, mejora de la imagen de marca, cumplimiento de normativas aduaneras y de comercio internacional.  
* Para el distribuidor y la tienda: eficiencia en la gestión de devoluciones y reclamos de garantía, reducción de riesgos de comercialización de productos falsificados, mejora de la imagen de marca, capacidad de ofrecer un valor añadido al cliente.  
* Para el consumidor: confianza en la autenticidad y el origen del dispositivo, acceso a información detallada sobre el historial del producto (compra en EE.UU., transporte, condiciones, despacho aduanero), capacidad de tomar decisiones de compra informadas, protección contra fraudes.  
* Para el comercio electrónico: reducción de la incertidumbre en la compra, aumento de las tasas de conversión, generación de datos valiosos sobre las preferencias del consumidor, diferenciación frente a la competencia.

## **2.2. Sistemas similares**

Existen en el mercado diversas soluciones que abordan la trazabilidad de productos con blockchain, con enfoques y alcances distintos. Ninguna de ellas está diseñada específicamente para el mercado boliviano de importación de dispositivos Apple, ni integra los procesos de compra en Estados Unidos, transporte internacional, despacho aduanero local y venta al consumidor en Bolivia, lo que constituye una oportunidad para el sistema propuesto.

* **IBM Food Trust (Internacional)**  
  Funcionalidades / Características: plataforma de trazabilidad blockchain para la industria alimentaria que permite rastrear productos desde la granja hasta la tienda. Ofrece visibilidad de la cadena de suministro, verificación de la autenticidad, gestión de retiros de productos y análisis de datos. Sus participantes incluyen productores, procesadores, distribuidores y minoristas.

  Desarrolladores: IBM.

  Licencia: propietaria, con modelos de suscripción para las empresas participantes.

  Distribución: web y API; el consumidor accede mediante código QR en el envase del producto.

  Aplicabilidad al proyecto: su enfoque en la trazabilidad de extremo a extremo y la verificación por parte del consumidor son aplicables, aunque está orientada a la industria alimentaria y no contempla las particularidades de la importación de productos electrónicos, como los identificadores IMEI, los números de serie de Apple o las condiciones de transporte de baterías de litio.

* **VeChain ToolChain (Global)**

Funcionalidades / Características: plataforma blockchain (vechainthor) que ofrece soluciones de trazabilidad para múltiples sectores, incluyendo alimentación, moda, lujo y farmacéutica. Permite asignar a cada producto un identificador digital único (código QR, NFC o RFID) que registra todo su ciclo de vida. Incluye herramientas para la gestión de la cadena de suministro, verificación de autenticidad y certificación de sostenibilidad.

Desarrolladores: VeChain Foundation.

Licencia: propietaria, con planes de pago según el volumen de transacciones.

Distribución: web, API y SDK para integración en aplicaciones y comercio electrónico.

Aplicabilidad al proyecto: su modelo de identificación única por producto y su integración con códigos QR son altamente relevantes. Sin embargo, no está especializada en dispositivos electrónicos, no integra números de serie o IMEI como identificadores nativos, y no considera los procesos aduaneros bolivianos ni la documentación específica de importación.

* **Aura Blockchain Consortium (Internacional)**

Funcionalidades / Características: consorcio fundado por LVMH, Prada y Cartier (Richemont) que ofrece una plataforma blockchain para la trazabilidad de productos de lujo. Cada producto lleva un chip NFC o código QR que permite al consumidor acceder a su "pasaporte digital": autenticidad, origen de los materiales, proceso de fabricación, certificaciones y todo el recorrido del artículo.

Desarrolladores: Aura Blockchain Consortium.

Licencia: privada, exclusiva para los miembros del consorcio.

Distribución: aplicación móvil y sitio web.

Aplicabilidad al proyecto: su concepto de "pasaporte digital" del producto es directamente aplicable al historial de trazabilidad de un dispositivo Apple. Sin embargo, su acceso es restringido a marcas de lujo miembros del consorcio, no contempla la importación desde EE.UU. ni los procesos aduaneros bolivianos, y no está disponible para importadores o tiendas independientes en Bolivia.

* **Seedtrace (Internacional)**

Funcionalidades / Características: plataforma blockchain especializada en la trazabilidad de alimentos y productos orgánicos. Permite a los productores gestionar datos, documentos y cuestionarios de trazabilidad; los registros quedan almacenados en blockchain y se ponen a disposición del consumidor mediante códigos QR en el envase o enlaces desde la tienda online.

Desarrolladores: Seedtrace GmbH.

Licencia: propietaria, con modelos de suscripción para productores.

Distribución: web y aplicación móvil.

Aplicabilidad al proyecto: su modelo de registro de eventos y visualización para el consumidor es aplicable, pero está enfocado en productos orgánicos y no en dispositivos electrónicos con identificadores técnicos como IMEI o número de serie.

* **TrustOS (Telefónica Tech) (Internacional)**

Funcionalidades / Características: plataforma blockchain industrial que ofrece trazabilidad de productos, autenticación digital y tokenización. Permite a las empresas registrar sus productos en la blockchain, generar identificadores digitales únicos y poner la información a disposición del consumidor.

Desarrolladores: Telefónica Tech.

Licencia: propietaria, con planes de pago empresariales.

Distribución: web, API y SDK.

Aplicabilidad al proyecto: su enfoque en la autenticación digital es relevante, pero su alcance es genérico y no aborda las necesidades específicas de la importación de dispositivos Apple a Bolivia ni la integración con números de serie, IMEI y EID.

* **Colmena DAO (Bolivia / Latinoamérica)**

Funcionalidades / Características: iniciativa de trazabilidad blockchain para la miel producida por pequeños apicultores en Bolivia, Colombia, Perú y Ecuador. Utiliza blockchain para registrar cada frasco de miel desde su origen, ofreciendo a los consumidores un historial verificable del producto.

Desarrolladores: Colmena DAO (startup).

Licencia: propietaria, en fase de piloto.

Distribución: web y código QR en el envase.

Aplicabilidad al proyecto: es la única solución con presencia en Bolivia, lo que demuestra la viabilidad de la trazabilidad blockchain en el mercado local. Sin embargo, su enfoque es exclusivamente agroalimentario y no contempla productos electrónicos ni procesos de importación internacional.

## **2.3. Casos de Estudio**

| Caso de Estudio | Empresa / Plataforma | Descripción | Enfoque / Impacto Principal |
| :---: | :---: | ----- | ----- |
| **Caso de Estudio 1** | **Aura Blockchain Consortium** | Consorcio fundado por LVMH, Prada y Cartier (Richemont) que implementa una plataforma blockchain para la trazabilidad de productos de lujo. Cada artículo recibe un chip NFC o código QR que permite al consumidor acceder a su "pasaporte digital" con información de autenticidad, origen de los materiales, proceso de fabricación y recorrido completo del artículo. La plataforma ha extendido su alcance a marcas como OTB Group (Diesel, Marni) y la empresa de cosméticos L'Oréal. | Autenticación y confianza del consumidor: La plataforma ha demostrado que la trazabilidad blockchain es un diferenciador clave en el mercado de bienes de alto valor, reduciendo significativamente la comercialización de productos falsificados. El "pasaporte digital" del producto se ha convertido en un estándar de transparencia para el consumidor de lujo, que exige verificar la autenticidad y el origen ético de sus compras. Lección aplicable: la asignación de un identificador digital único a cada unidad de producto (chip NFC o código QR) y la exposición del historial completo al consumidor son prácticas directamente trasladables a la trazabilidad de dispositivos Apple. |
| **Caso de Estudio 2** | **VeChain ToolChain** | Plataforma blockchain (vechainthor) utilizada por marcas como BMW, Renault y Walmart China para la trazabilidad de componentes y productos en sus cadenas de suministro. En el sector automotriz, VeChain ha implementado la trazabilidad de baterías de vehículos eléctricos, registrando su origen, condiciones de transporte y ciclo de vida. En electrónica de consumo, ha permitido a fabricantes chinos rastrear dispositivos desde la fábrica hasta el consumidor, verificando la autenticidad y el cumplimiento de estándares de calidad. | Logística internacional y condiciones de transporte: La plataforma ha demostrado la viabilidad de registrar condiciones ambientales (temperatura, humedad) durante el transporte de componentes electrónicos sensibles. Para baterías de litio —presentes en todos los dispositivos Apple—, el monitoreo de condiciones de transporte es crítico para prevenir accidentes y garantizar la integridad del producto. Lección aplicable: la integración de sensores de temperatura, humedad y vibración en la cadena logística, con registro en blockchain, es una funcionalidad que el sistema propuesto debe incorporar para garantizar la calidad de los dispositivos importados. |
| **Caso de Estudio 3** | **Everledger (plataforma) / Caso de importación de diamantes** | Everledger es una plataforma blockchain que comenzó rastreando diamantes desde su origen en minas hasta el consumidor final, registrando cada transacción y certificación en la cadena de bloques. Posteriormente, extendió su modelo a productos de lujo, dispositivos electrónicos y obras de arte. En el contexto de importación, Everledger ha trabajado con aduanas y transportistas internacionales para documentar el recorrido de productos de alto valor a través de fronteras, proporcionando a los consumidores un historial verificable que incluye certificados de autenticidad, condiciones de transporte y documentación aduanera. | mportación internacional y documentación aduanera: El caso demuestra que la trazabilidad blockchain puede integrarse con los procesos de importación, registrando documentos clave (facturas comerciales, certificados de origen, guías aéreas) y vinculándolos al identificador único del producto. Esto reduce el riesgo de fraude documental, agiliza los procesos aduaneros y proporciona al consumidor final la certeza de que el producto ha sido importado legalmente. Lección aplicable: el sistema propuesto debe integrar la documentación de importación (facturas de compra en EE.UU., guías de transporte, documentos aduaneros) como parte del historial de trazabilidad del dispositivo, visible para el consumidor. |

# **3\. DESCRIPCIÓN DEL PROBLEMA**

En el mercado actual de dispositivos móviles, la distancia entre el fabricante (Apple Inc.) y el consumidor final en Bolivia se ha ampliado considerablemente debido a la importación paralela, el auge del comercio electrónico de productos reacondicionados y la falta de canales oficiales de distribución en el país. Esta distancia geográfica, logística y de información genera una serie de problemas críticos que afectan a todos los actores de la cadena de valor del iPhone:

**Para el importador/distribuidor de iPhones en Bolivia**

* No puede garantizar la autenticidad del dispositivo al consumidor. El importador adquiere cargamentos de iPhones desde Estados Unidos (muchas veces a través de intermediarios) sin contar con un registro digital que certifique que cada unidad es original y no ha sido manipulada, reparada con piezas genéricas o reacondicionada sin control de calidad.  
* Cuando un lote presenta problemas (baterías hinchadas, pantallas que se despegan, fallas en el Face ID), el importador no puede identificar rápidamente el origen del problema (¿fue en fábrica, durante el transporte, en almacenaje o en la manipulación de terceros?) ni localizar a todos los consumidores que adquirieron unidades de ese lote específico, exponiéndose a reclamaciones masivas y pérdida de reputación.  
* La falta de trazabilidad verificable impide que el importador pueda cobrar una prima por iPhones "100% originales" o "certificados", ya que el consumidor no tiene forma de verificar esa afirmación más allá de la palabra del vendedor, lo que iguala en el mercado a dispositivos originales con réplicas o reparados.  
* En caso de falsificaciones, el importador no cuenta con evidencia digital (hash en blockchain, historial inmodificable) que demuestre que el iPhone que él comercializa es auténtico, lo que lo deja indefenso ante acusaciones de comercializar productos falsificados.  
* No puede demostrar el estado de la batería ni el historial de reparaciones. El importador recibe iPhones usados o reacondicionados sin un registro histórico del porcentaje de salud de batería, cambios de pantalla, reparaciones de puerto de carga o sustituciones de cristal trasero, lo que genera desconfianza y devoluciones.

**Para la tienda online (marketplace o e-commerce especializado)**

* Recibe iPhones del importador sin un registro histórico completo, lo que le impide verificar si durante el transporte marítimo o aéreo desde Miami o Panamá se respetaron las condiciones adecuadas (temperatura, humedad, vibraciones), factores críticos para la integridad de las baterías de litio y los componentes electrónicos sensibles.  
* Cuando se detecta un problema como iPhones que no encienden, con IMEI bloqueado por robo en EE.UU., o con baterías que se inflan a los pocos días, la tienda debe rastrear manualmente qué proveedor entregó ese lote, a qué almacén llegó, y qué cliente lo compró. Este proceso puede tomar días o semanas, exponiendo a los consumidores a riesgos y generando una avalancha de reclamos.  
* La gestión de devoluciones es un caos. El consumidor devuelve un iPhone diciendo que "no es original" o que "la batería dura menos de lo esperado", pero la tienda no puede verificar si el dispositivo que le devuelven corresponde efectivamente al que ella vendió (número de serie, IMEI, estado físico), o si fue sustituido por una réplica durante el proceso de devolución.  
* La tienda online no puede ofrecer a sus clientes información más allá de la ficha técnica (pantalla, cámara, almacenamiento). No puede mostrar el historial completo de ese iPhone específico: país de origen, fecha de fabricación, número de ciclos de carga reales, reparaciones previas, o si ha sido reportado como robado. Esto limita la diferenciación y la construcción de confianza en un mercado saturado de ofertas.  
* No puede justificar el precio. Un iPhone "reacondicionado premium" puede costar el doble que uno "reacondicionado estándar", pero sin trazabilidad, la tienda no puede demostrar por qué cobra ese precio adicional (batería nueva original, pantalla original, garantía extendida, etc.), lo que genera desconfianza y pérdida de ventas.

**Para el consumidor final en Bolivia**

* Compra un iPhone por internet sin poder verificar su autenticidad. El consumidor recibe una caja, abre el dispositivo y conecta a iTunes, pero no tiene forma de saber si ese iPhone ha sido reparado con piezas genéricas, si su IMEI ha sido manipulado, si fue robado en otro país, o si su batería es original o de reemplazo de baja calidad.  
* En el comercio electrónico, esta incertidumbre es aún mayor. El consumidor no puede inspeccionar físicamente el iPhone antes de comprarlo; solo confía en fotos y descripciones que pueden ser engañosas. No sabe si el "iPhone 15 Pro Max" que está comprando es realmente un dispositivo de exhibición, un reacondicionado de tercer nivel o una réplica china con interfaz modificada.  
* Cuando el iPhone resulta defectuoso (pantalla que se despega, cámara con manchas, batería que se calienta), el consumidor no tiene forma de rastrear su origen para saber si su caso es aislado o parte de un problema más amplio del lote, y la tienda online suele evadir responsabilidades diciendo que "el dispositivo fue manipulado por el usuario".  
* El consumidor que desea tomar decisiones de compra informadas (batería con más del 90% de salud, pantalla original, sin reparaciones previas, garantía extendida) no dispone de información confiable para hacerlo. Todas las tiendas online ofrecen descripciones genéricas que no se pueden verificar de forma independiente.  
* No recibe ninguna información sobre el recorrido del iPhone después de su compra. Una vez que el dispositivo llega a sus manos, la relación con la tienda o el importador termina. No hay un canal que le permita consultar el historial del dispositivo, registrar una incidencia, o verificar si su unidad ha sido incluida en algún retiro de producto o alerta de seguridad (ej. baterías con riesgo de incendio).  
* El consumidor no puede verificar el estado de la garantía. Muchos iPhones importados conservan garantía internacional de Apple, pero el consumidor no sabe cómo verificar el tiempo restante ni si su dispositivo es elegible para reparación en un centro autorizado. Esto genera incertidumbre y desconfianza en el mercado de segunda mano.

**Para la plataforma de comercio electrónico (marketplace)**

* No puede ofrecer a sus clientes un valor diferenciado en términos de transparencia y confianza para iPhones. Todas las tiendas online ofrecen los mismos modelos, las mismas fotos de stock y descripciones genéricas; la plataforma no tiene cómo destacar que un dispositivo tiene "trazabilidad verificada" o "certificado de autenticidad con blockchain".  
* La tasa de abandono del carrito sigue siendo alta porque el consumidor duda de la autenticidad del iPhone. Ante la incertidumbre, el usuario prefiere no comprar o busca opciones en tiendas físicas donde puede probar el dispositivo antes de pagar, lo que reduce las conversiones del e-commerce.  
* Carece de datos sobre el comportamiento del consumidor en relación con la trazabilidad. La plataforma no sabe si los usuarios valoran más la garantía, la autenticidad, el estado de la batería o el historial de reparaciones, lo que limita su capacidad de personalización y segmentación para ofrecer iPhones con atributos específicos a diferentes perfiles de comprador.  
* En caso de retiros de productos o alertas de seguridad (baterías defectuosas de un lote específico, reportes de incendio, bloqueos por IMEI robado), la plataforma no puede notificar automáticamente a los consumidores afectados porque no tiene registrado qué unidad específica compró cada usuario ni tiene un canal de comunicación posventa activo.  
* La plataforma no puede prevenir el fraude de devoluciones. Los estafadores compran un iPhone original, lo sustituyen por una réplica dentro de la caja, y solicitan la devolución del dinero. Sin un registro de trazabilidad que vincule el número de serie/IMEI del dispositivo enviado con el recibido en la devolución, la plataforma asume pérdidas y termina perjudicando a vendedores legítimos.

# **4\. OBJETIVOS**

### **4.1. Objetivo General**

Desarrollar una Plataforma Web y Aplicación Móvil para la Trazabilidad de Dispositivos Apple mediante Tecnología Blockchain, desde el Origen hasta el Consumidor Final. 

### **4.2. Objetivos Específicos**

* Recolectar información sobre los procesos actuales de importación, distribución, venta y postventa de dispositivos Apple en Bolivia, mediante entrevistas con importadores, distribuidores y consumidores, con el fin de identificar los requerimientos funcionales y no funcionales del sistema a implementar.  
* Recopilar y analizar información sobre las tecnologías blockchain, contratos inteligentes y mecanismos de identificación digital (código QR, NFC, número de serie, IMEI) existentes, con el fin de seleccionar las herramientas más adecuadas para garantizar la inmutabilidad y trazabilidad de los registros del sistema.  
* Implementar un sistema centralizado de gestión de información, mediante una API REST desarrollada en FastAPI y una base de datos PostgreSQL, que permita registrar y administrar los datos relacionados con productos, lotes, actores de la cadena de suministro y eventos logísticos.  
* Registrar de manera inmutable los eventos críticos de la cadena de custodia de cada dispositivo, mediante contratos inteligentes desarrollados en Solidity sobre una red blockchain, vinculando cada unidad física a su historial digital mediante código QR o etiqueta NFC.  
* Verificar la autenticidad de los dispositivos, comparando el número de serie e IMEI registrado con la información almacenada en blockchain, para alertar al consumidor ante posibles falsificaciones o irregularidades.  
* Exponer los datos de trazabilidad del producto mediante una API REST documentada, que permita su integración con plataformas externas de comercio electrónico para la visualización del historial dentro de la ficha del producto.  
* Desplegar las interfaces web y móvil del sistema, desarrolladas en Angular y Flutter respectivamente, en un entorno de nube mediante contenedores Docker, permitiendo a los administradores y distribuidores gestionar la cadena de suministro, y al consumidor final escanear y consultar el historial de su dispositivo.

# **5\. ALCANCE**

Durante el semestre se desarrollará una plataforma funcional que cubra el ciclo completo de la trazabilidad de dispositivos móviles Apple importados: desde la compra a proveedores en Estados Unidos, el transporte internacional, la recepción y el despacho aduanero en Bolivia, la identificación individual de cada unidad mediante número de serie, IMEI o EID, el almacenamiento, los traslados logísticos, la venta al consumidor final y la gestión de postventa (devoluciones, garantías y documentos adjuntos), integrando cada evento crítico con un registro inmutable en blockchain. 

El sistema está diseñado bajo una arquitectura multiempresa (multi-tenant), lo que permite que múltiples importadoras, distribuidoras y tiendas operen sobre la misma plataforma de forma completamente aislada y segura, compartiendo la infraestructura pero manteniendo la independencia de sus datos y operaciones. El acceso a cada funcionalidad está determinado por seis roles con cuenta en el sistema, además de participantes externos de la cadena de suministro sin cuenta (Proveedor en EE.UU., Transportista Internacional y Aduana) y del acceso público sin registro para la verificación de autenticidad. 

El alcance se organiza en los siguientes módulos, que constituirán la base del Product Backlog y se distribuirán entre los sprints planificados. Cada módulo está alineado con las entidades del modelo de datos y cubre una fase específica del ciclo de vida del producto.

## **5.1.1. Módulo de seguridad y multi-tenant**

Este módulo permitirá gestionar el acceso a la plataforma y la administración de las empresas que operan sobre ella, garantizando que cada usuario acceda únicamente a la información y funciones correspondientes a su rol y a su empresa.  
**Funcionalidades**:

* Registro e inicio de sesión mediante credenciales, con generación y renovación de tokens JWT.  
* Recuperación de contraseña mediante verificación por correo electrónico.  
* Creación, edición y desactivación de cuentas de usuario según rol (Super Administrador, Administrador de Empresa, Gestor de Operaciones, Gestor de Ventas y Postventa, Consumidor Registrado, Auditor).  
* Creación, configuración y suspensión de empresas (tenants) por parte del Super Administrador.  
* Aislamiento de datos entre empresas, aun cuando compartan la misma infraestructura.  
* Registro de bitácora de accesos y actividades sensibles para supervisión y auditoría.  
* Consulta de la bitácora por parte del Super Administrador (a nivel global) y del Auditor (con fines de cumplimiento normativo).

## **5.1.2. Módulo de catálogo y certificaciones**

Este módulo permitirá administrar la información de los productos Apple comercializados por cada empresa, junto con las certificaciones técnicas que respaldan su autenticidad y calidad. 

**Funcionalidades**:

* Registro y edición de productos del catálogo (iPhone, MacBook, iPad, accesorios), incluyendo modelo, especificaciones técnicas, capacidad y color.  
* Gestión de categorías y atributos diferenciadores de los productos.  
* Asociación de certificaciones técnicas (FCC, CE, RoHS, Energy Star) y de la garantía internacional del fabricante a cada producto.  
* Consulta del catálogo por parte del Consumidor Registrado y de visitantes sin cuenta antes de la compra.

## **5.1.3. Módulo de abastecimiento e importación**

Este módulo permitirá gestionar el proceso de compra de dispositivos a proveedores en Estados Unidos y su recepción en el país tras el despacho aduanero.

**Funcionalidades:**

* Registro de órdenes de compra a proveedores en el extranjero.  
* Flujo de aprobación de órdenes de compra por parte del Administrador de Empresa.  
* Registro de la recepción de mercancía en almacén tras su despacho aduanero.  
* Consulta del estado de las órdenes de compra en curso.

## **5.1.4. Módulo de Actores y Ubicaciones**

Este módulo permitirá representar a los participantes externos de la cadena de suministro y las ubicaciones físicas involucradas en el proceso logístico, sin que dichos participantes requieran una cuenta en el sistema.

**Funcionalidades**:

* Registro y administración de participantes externos: Proveedor en EE.UU., Transportista Internacional y Aduana.  
* Registro y administración de ubicaciones físicas (almacenes, puertos de entrada, oficinas aduaneras).  
* Asociación de estos actores y ubicaciones a los eventos de trazabilidad correspondientes.

## **5.1.5. Módulo de inventario y trazabilidad**

Constituye el eje central de la plataforma y permitirá identificar cada unidad de forma individual, registrar su recorrido a lo largo de la cadena de suministro y construir su historial completo de trazabilidad.

**Funcionalidades**:

* Registro de unidades individuales mediante número de serie, IMEI o EID, vinculadas a su orden de compra.  
* Generación automática de códigos QR o etiquetas NFC únicos por unidad.  
* Escaneo de códigos QR/NFC desde la aplicación móvil, tanto por el Consumidor y visitantes sin cuenta como por el Gestor de Operaciones al recibir mercancía.  
* Registro de movimientos logísticos (origen, destino, fechas, responsable) de cada unidad o envío.  
* Registro de condiciones de transporte (temperatura, humedad, vibración), de forma manual o mediante sensores IoT.  
* Registro de incidencias ocurridas durante el transporte, el despacho aduanero o el almacenamiento.  
* Construcción y consulta del historial cronológico completo de cada unidad, con mapa interactivo del recorrido.  
* Verificación de autenticidad del producto a partir de sus registros de trazabilidad, disponible también para visitantes sin cuenta.  
* Verificación automática mediante visión por computadora del código QR/NFC escaneado, para detectar posibles falsificaciones o alteraciones del identificador.  
* Reporte de sospecha de falsificación o irregularidad por parte del Consumidor.  
* Exposición del historial de trazabilidad y del estado de verificación mediante una API REST documentada (OpenAPI/Swagger), autenticada con API key, para que plataformas de comercio electrónico externas consulten y muestren esta información dentro de su ficha de producto, sin gestionar el proceso de compra. 

## **5.1.6. Módulo de ventas**

Este módulo registrará la venta de unidades como un evento más de la cadena de trazabilidad, asociando cada transacción comercial —ya procesada externamente por la tienda o el punto de venta— a la unidad física correspondiente, sin gestionar el procesamiento del pago. 

**Funcionalidades**:

* Registro del evento de venta de una unidad específica al consumidor final (fecha, empresa vendedora, canal de venta).  
* Asignación de la unidad física (por serial/IMEI) a la transacción de venta correspondiente.  
* Registro del estado de la transacción como referencia informativa (ej. "completada", "anulada"), sin integración con pasarelas de pago.  
* Consulta del historial de ventas por parte del Gestor de Ventas y Postventa y del Administrador de Empresa.

## **5.1.7. Módulo de postventa**

Gestionará la relación con el consumidor después de la venta, cubriendo devoluciones, garantías y documentación asociada a cada unidad.

**Funcionalidades**:

* Registro de devoluciones asociadas a una unidad específica.  
* Gestión y consulta del estado de garantía por número de serie.  
* Adjunto de documentos de respaldo (facturas, certificados) a cada unidad.  
* Consulta por parte del Consumidor del estado de sus garantías y del historial de sus compras.  
* Guardado de productos como favoritos y notificaciones sobre incidencias o retiros relacionados con sus unidades.

## **5.1.8. Módulo de blockchain (registro inmutable)**

Registrará de forma inmutable y descentralizada los eventos críticos de la cadena de trazabilidad, garantizando que la información no pueda ser alterada retrospectivamente.

**Funcionalidades**:

* Registro en blockchain de eventos críticos: compra, despacho aduanero, movimientos, entrega y venta.  
* Generación de hash y marca de tiempo verificable para cada evento registrado.  
* Confirmación visual al usuario del envío del evento a blockchain, con estado "pendiente" hasta su confirmación en red.  
* Consulta y verificación de integridad de los registros blockchain por parte del Auditor y el Super Administrador.  
* Generación automática de certificados digitales de trazabilidad al momento de la venta, respaldados por los registros en blockchain.  
* Visualización y descarga de certificados digitales en formato PDF.  
* Generación de reportes e indicadores de trazabilidad, incidencias, ventas y cumplimiento normativo, con filtros por periodo y exportación de datos.

# **6\. ELEMENTOS DEL SIBC**

Un Sistema de Información Basado en Computadoras (SIBC) para este proyecto integra cinco componentes fundamentales que trabajan en conjunto para cumplir con los objetivos de trazabilidad.

1. **Hardware:** 

   Infraestructura física que incluye equipos de desarrollo de alto rendimiento (16GB+ RAM, SSD NVMe) y dispositivos móviles para la lectura de códigos QR/NFC durante las pruebas del sistema. La implementación considera servicios de infraestructura como servicio (IaaS) sobre Google Cloud Platform para garantizar la escalabilidad y alta disponibilidad del backend, la base de datos y el almacenamiento de archivos. Se contemplan terminales móviles para el Gestor de Operaciones, utilizados en la recepción de mercancía y el registro de eventos de trazabilidad en almacén, así como para el Consumidor Registrado y el Visitante Anónimo en la consulta del historial de un dispositivo mediante escaneo.

2. **Software:**  
   Conjunto de aplicaciones que integran el sistema: backend con API REST desarrollada en FastAPI, frontend web en Angular para administración y gestión, aplicación móvil en Flutter para consumidores, sistema gestor de base de datos PostgreSQL, y plataforma blockchain con smart contracts. Se incluyen herramientas de integración con sistemas ERP existentes.

3. **Datos:**  
   Información estructurada y no estructurada: datos maestros (usuarios, productos, lotes, certificaciones), datos transaccionales (eventos de la cadena de suministro, movimientos logísticos, incidencias), y registros inmutables en blockchain (hashes, timestamps, metadatos). Se contempla almacenamiento off-chain para archivos grandes como imágenes y documentos.

4. **Procesos:**  
   Procedimientos operativos definidos: registro de productos y lotes, actualización de estados en la cadena de suministro, generación de códigos QR/NFC, consulta de historial por parte del consumidor, emisión de certificados digitales de trazabilidad, y gestión de alertas y notificaciones. La automatización se gestiona mediante smart contracts.

5. **Recursos Humanos:**  
   Equipo multidisciplinario conformado por Product Owner, Scrum Master, desarrolladores especializados (backend en FastAPI, frontend web en Angular, aplicación móvil en Flutter, y desarrollo de smart contracts en Solidity), equipo de pruebas (QA), administradores del sistema y personal de soporte técnico. Se incluye la figura del desarrollador blockchain, responsable del despliegue y mantenimiento de los smart contratos sobre la red Ethereum, así como de la integración entre el backend y la testnet utilizada durante el desarrollo del proyecto.

# **7\. TECNOLOGÍA**

La selección tecnológica responde a los requerimientos del sistema, considerando la necesidad de escalabilidad, seguridad e integración con blockchain.

## **7.1. Para el Desarrollo**

| Componente | Tecnología Propuesta | Justificación |
| :---- | :---- | :---- |
| Backend / API | FastAPI (Python) | Framework moderno y de alto rendimiento para construir APIs REST con documentación automática (OpenAPI). Ofrece validación de datos mediante Pydantic, soporte nativo para async/await, e integración eficiente con PostgreSQL y WebSockets para notificaciones en tiempo real.  |
| Frontend Web | Angular (TypeScript) | Framework robusto para aplicaciones web empresariales. Su arquitectura basada en componentes permite construir dashboards administrativos y operativos para los distintos roles del sistema (Super Administrador, Administrador de Empresa, Gestor de Operaciones, Gestor de Ventas y Postventa).  |
| Aplicación Móvil | Flutter (Dart) | Framework de Google para desarrollo multiplataforma (iOS y Android) con una única base de código. Utilizado para la aplicación de escaneo de códigos QR/NFC y consulta del historial de trazabilidad por parte del Consumidor Registrado y el Gestor de Operaciones.  |
| Base de Datos | PostgreSQL | Sistema de base de datos relacional robusto, con transacciones ACID e índices JSONB, utilizado para almacenar la información operativa del sistema: usuarios, empresas, catálogo, órdenes de compra, unidades y eventos logísticos.  |
| Blockchain | Ethereum  | Red blockchain pública utilizada para el registro inmutable de los eventos críticos de trazabilidad (compra, despacho aduanero, movimientos, venta), mediante contratos inteligentes desarrollados en Solidity.  |
| Almacenamiento Off-Chain | Google Cloud Storage | Almacenamiento para archivos pesados (imágenes de productos, documentos, certificados digitales), evitando sobrecargar la blockchain con datos que no requieren inmutabilidad directa.  |
| Smart Contracts | Solidity (Ethereum)  | Programas auto-ejecutables para automatizar la verificación de autenticidad, la emisión de certificados digitales y la generación de alertas ante incidencias.  |
| Comunicación con Blockchain  | Web3.py  | Librería de Python utilizada por el backend (FastAPI) para enviar transacciones, invocar funciones de los smart contracts y consultar el estado de la red Ethereum.  |
| Modelado de Software | Modelo C4 | Estándar para documentar arquitectura de software en cuatro niveles de abstracción (Contexto, Contenedores, Componentes, Código), facilitando la comunicación técnica y no técnica. |
| Herramienta de Modelado | Enterprise Architect | Herramienta profesional para diseño UML y modelado de sistemas complejos. Permite documentar casos de uso, diagramas de clases y secuencia. |
| Entorno de Desarrollo | Visual Studio Code / PyCharm / Android Studio | IDEs con soporte para depuración, control de versiones y extensiones para desarrollo web, móvil y blockchain. Android Studio para emulación de Flutter. |
| Colaboración y Gestión de Proyectos | Jira Software | Jira para gestión de proyectos con marco SCRUM; Confluence para documentación colaborativa del proyecto y especificaciones técnicas. |
| Control de Versiones | Git / GitHub  | Sistema de control de versiones distribuido para gestionar el código fuente, con flujo de trabajo basado en ramas y GitHub como repositorio remoto centralizado del proyecto.  |
| Pruebas Automatizadas | Pytest (FastAPI), Jest/Karma (Angular), Flutter Test | Frameworks para pruebas unitarias, de integración y end-to-end. Pytest para backend, Jest para Angular, y Flutter Test para la aplicación móvil. |
| Comunicación en Tiempo Real | WebSockets / Socket.IO | Para notificaciones push en tiempo real, actualización de estados de trazabilidad y alertas a usuarios. |
| Autenticación y Autorización | JWT (JSON Web Tokens) \+ OAuth2 | Mecanismo seguro para autenticación de usuarios y gestión de permisos por roles (productor, distribuidor, consumidor, administrador). |

## **7.2. Para la Puesta en Marcha**

| Componente | Tecnología Propuesta | Justificación |
| ----- | ----- | ----- |
| Infraestructura en la Nube | Google Cloud Platform (GCP) | Plataforma en la nube utilizada para desplegar y gestionar el backend, la base de datos y el almacenamiento del sistema, con modelo de pago por uso y escalabilidad según demanda. |
| Servidor de Aplicación | Compute Engine | Instancias para desplegar el backend desarrollado en FastAPI, con posibilidad de autoescalado y balanceo de carga según el volumen de solicitudes. |
| Base de Datos | Cloud SQL para PostgreSQL | Servicio de base de datos gestionado, con alta disponibilidad, copias de respaldo automáticas y escalabilidad. |
| Red Blockchain | Testnet de Ethereum (Sepolia / Amoy) | Red de prueba pública utilizada para el registro de eventos y la ejecución de smart contracts sin incurrir en costos reales de transacción (gas fees), adecuada para el entorno académico del proyecto. |
| Almacenamiento de Archivos | Cloud Storage | Almacenamiento seguro y escalable para imágenes, certificados digitales y documentos asociados a cada unidad. |
| Distribución de Contenido | Cloud CDN | Red de distribución de contenido para servir archivos estáticos (imágenes, CSS, JS) con baja latencia a los usuarios de la plataforma web. |
| Seguridad | HTTPS (SSL/TLS), Google Cloud Armor | Protocolos y servicios para garantizar la integridad y confidencialidad de los datos en tránsito y en reposo, junto con protección ante accesos no autorizados. |
| Monitorización | Cloud Monitoring | Supervisión del rendimiento, la disponibilidad y las alertas de la infraestructura desplegada, con dashboards para el equipo. |
| Gestión de Logs | Cloud Logging | Centralización y análisis de los registros de actividad de la aplicación y la infraestructura, para depuración y auditoría. |
| Gestión de Claves | Google Cloud KMS / Secret Manager | Almacenamiento seguro de claves criptográficas utilizadas para firmar transacciones en la red Ethereum, y de credenciales sensibles del sistema. |
| CI/CD | GitHub Actions | Automatización de pruebas, construcción y despliegue continuo de los componentes backend, web y móvil. |
| Orquestación de Contenedores | Docker | Empaquetado de los servicios de la aplicación para su despliegue portable dentro de Google Cloud Platform. |
| Servicio de Notificaciones | Firebase Cloud Messaging (FCM) | Envío de notificaciones push a la aplicación móvil ante alertas y actualizaciones de trazabilidad. |
| Balanceador de Carga | Cloud Load Balancing | Distribución del tráfico entre instancias de aplicación para garantizar alta disponibilidad y rendimiento. |

# **8\. Costos para la puesta en marcha**

La estimación de costos se ha estructurado en base a los componentes del SIBC, considerando las tecnologías seleccionadas y referencias de implementaciones similares en proyectos de trazabilidad blockchain. Los costos son aproximados y pueden variar según el alcance, tamaño de la empresa y región.

## **8.1. Hardware**

| Ítem | Descripción | Costo Estimado (USD) |
| ----- | ----- | ----- |
| Servidores de Aplicación (Compute Engine) | Instancias para el backend FastAPI, con autoescalado según demanda. Especificaciones: 4 vCPUs, 16 GB RAM. Incluye balanceo de carga (Cloud Load Balancing). | $300 \- $700 |
| Base de Datos (Cloud SQL) | Instancia gestionada de PostgreSQL con alta disponibilidad y copias de respaldo automáticas. | $450 \- $1,200 |
| Almacenamiento (Cloud Storage) | Almacenamiento para imágenes, certificados digitales y documentos de productos (estimado 1-5 TB con redundancia). | $50 \- $200 |
| Distribución de Contenido (Cloud CDN) | Servicio para entregar archivos estáticos (imágenes, CSS, JS) con baja latencia. | $20 \- $100 |
| Equipos de Desarrollo | (Costo único amortizado a 36 meses) Computadoras de alto rendimiento para el equipo: 32GB+ RAM, SSD NVMe 1TB, procesador i7/i9 o equivalente (6 equipos). | $333 \- $500 (amortizado) |
| Dispositivos Móviles de Prueba | (Costo único amortizado a 24 meses) Dispositivos iOS y Android para pruebas de la aplicación Flutter. | $125 \- $250 (amortizado) |

## **8.2. Software**

Los costos de software incluyen las herramientas y plataformas necesarias para el funcionamiento del sistema.

| Ítem | Descripción | Costo Estimado (USD/mes) |
| ----- | ----- | ----- |
| Licencias de Desarrollo | IDE profesionales, herramientas de modelado (Enterprise Architect). | $100 \- $400 |
| Costos de Nube (Google Cloud Platform) | Compute Engine, Cloud SQL, Cloud Storage, Cloud CDN, Cloud Load Balancing, redes y monitorización básica. | $1,500 \- $2,500 |
| Costos de Red Blockchain (Ethereum) | Uso de testnet pública (Sepolia/Amoy) sin costo real durante desarrollo y pruebas. Estimación referencial de gas fees en mainnet. En Ethereum: variable según congestión. Estimado para volumen inicial de 10,000 transacciones/mes. | $50 \- $800 (variable en mainnet) |
| Herramientas de Colaboración | Jira (Business Class, 6-8 usuarios) \+ GitHub Team. | $100 \- $250 |
| Certificados SSL y Seguridad | Certificados SSL/TLS, Google Cloud Armor, protección DDoS. | $80 \- $250 |
| Servicio de Notificaciones | Firebase Cloud Messaging (gratuito hasta límites generosos). | $50 \- $200 |
| Servicio de CI/CD | GitHub Actions. | $100 |
| Monitorización y Logs | Cloud Monitoring y Cloud Logging. | $100 |

## **8.3. Comunicaciones**

| Ítem | Descripción | Costo Estimado (USD/mes) |
| :---- | :---- | :---- |
| Ancho de Banda y Tráfico de Red | Transferencia de datos entre nodos blockchain, aplicaciones y usuarios finales. Depende del volumen de transacciones y usuarios activos (estimado inicial 1,000-5,000 usuarios). | $80  |
| Servicio de Push Notifications | Firebase Cloud Messaging (FCM) para notificaciones push en aplicación Flutter (gratuito hasta 100,000 mensajes/día). | $50 |

## **8.4. Humanos**

| Ítem | Descripción | Costo Estimado (USD/mes) |
| :---- | :---- | :---- |
| Product Owner | Definición y priorización de requisitos, gestión del Product Backlog, comunicación con stakeholders. | $2,900  |
| Scrum Master | Facilitación del proceso ágil, eliminación de impedimentos, coordinación de eventos SCRUM, gestión del tablero Trello. | $2,500  |
| Desarrolladores Backend (FastAPI) | 2 desarrolladores: API REST, lógica de negocio, integración con blockchain, WebSockets y base de datos PostgreSQL. | $6,700  |
| Desarrolladores Frontend Web (Angular) | 2 desarrolladores: plataforma web para administración, productores y distribuidores, dashboards interactivos. | $6,700  |
| Desarrolladores Móvil (Flutter) | 2 desarrolladores: aplicación para consumidores, escaneo de códigos QR, integración con API, notificaciones push. | $6,700  |
| Desarrollador Blockchain | 1 desarrollador: desarrollo y despliegue de smart contracts (Solidity), integración entre FastAPI y la red Ethereum mediante Web3.py.  | $5,000  |

## **8.5. Logística**

Los costos logísticos abarcan los aspectos organizativos necesarios para planificar, coordinar y ejecutar la implementación del sistema.

| Ítem | Descripción | Costo Estimado (USD/mes) |
| :---- | :---- | :---- |
| Capacitación de Usuarios | Talleres y sesiones de formación para productores, distribuidores y administradores sobre uso del sistema, beneficios de blockchain y trazabilidad. Materiales didácticos incluidos. (3 meses) | $1,700 |
| Migración de Datos | Proceso de migración y limpieza de datos existentes (productos, lotes, proveedores) desde sistemas legacy, hojas de cálculo o documentos físicos. (2 meses) | $5,000 |
| Documentación y Manuales | Elaboración de manuales de usuario, guías de instalación, documentación técnica de API, y guías de administración del sistema. (2 meses) | $1,000 |
| Pruebas Piloto | Implementación piloto con un grupo reducido de productores y distribuidores para validar el sistema antes del lanzamiento completo. (1 mes) | $3,000 |

# **9\.  Beneficios para el cliente**

La implementación de este sistema de trazabilidad blockchain con las tecnologías Fast API, Angular, PostgreSQL y Flutter genera beneficios cuantificables que impactan directamente en la eficiencia operativa, la confianza del consumidor y la competitividad de la empresa.

## **9.1. Tiempo**

| Beneficio | Descripción | Impacto Cuantificado |
| :---- | :---- | :---- |
| Reducción en Retiros de Producto | Identificación y localización rápida de unidades afectadas por un problema específico (por ejemplo, baterías de un mismo envío con condiciones de transporte anómalas) mediante consultas optimizadas en PostgreSQL y registros inmutables en blockchain. Reducción del tiempo de reacción de semanas a horas o minutos.  | Reducción del tiempo de gestión de retiros en un 99.97% |
| Optimización de la Cadena de Suministro | Identificación de cuellos de botella y retrasos logísticos mediante análisis de datos en tiempo real. Permite la corrección proactiva y reducción de tiempos de entrega. | Reducción de pasos en procesos de exportación en un 40% |
| Automatización de Procesos Administrativos | Los smart contracts automatizan verificación de autenticidad, emisión de certificados y generación de alertas. FastAPI procesa solicitudes en milisegundos. | Reemplazo de semanas de trabajo manual por minutos |
| Desarrollo Ágil con FastAPI | FastAPI permite desarrollo rápido de APIs con documentación automática, reduciendo tiempo de desarrollo backend en comparación con frameworks tradicionales. | Reducción del tiempo de desarrollo en un 30-40% |

## **9.2. Esfuerzo humano** 

| Beneficio | Descripción | Impacto Cuantificado |
| :---- | :---- | :---- |
| Reducción de Errores Humanos | Automatización del registro de eventos mediante validaciones en FastAPI (Pydantic) y Flutter, eliminación de registros manuales y conciliación de datos. | Eliminación del 99.9% de errores manuales en gestión documental |
| Eficiencia Operativa | Digitalización y automatización del control de trazabilidad, desde origen hasta consumidor final. Interfaz intuitiva en Angular y Flutter reduce curva de aprendizaje. | Incremento de eficiencia operativa del 85% |
| Reducción de Litigios y Reclamaciones | Registros inmutables en blockchain y verificables reducen disputas con proveedores y reclamaciones de consumidores. | Disminución significativa de litigios y reclamaciones |
| Cumplimiento Normativo Automatizado | Verificación automática de certificaciones técnicas y de importación (FCC, CE, RoHS, garantía internacional del fabricante) mediante smart contracts. Auditorías simplificadas gracias a la trazabilidad completa del proceso de importación y comercialización.  | Cumplimiento normativo del 99.9% |
| Desarrollo Multiplataforma con Flutter | Un solo código base para iOS y Android reduce el esfuerzo de desarrollo y mantenimiento de la aplicación móvil en comparación con desarrollo nativo separado. | Reducción del esfuerzo de desarrollo móvil en un 40-50% |

## **9.3. Costos**

| Beneficio | Descripción | Impacto Cuantificado |
| :---- | :---- | :---- |
| Reducción de Costos Operativos | Disminución de costos asociados a gestión manual, devoluciones, retiros de productos, y mermas por caducidad o condiciones inadecuadas. PostgreSQL optimiza consultas reduciendo costos de infraestructura. | Reducción de hasta 35.2% del Costo Total de Propiedad (TCO) |
| Menor Costo de Gestión Documental | Eliminación de documentos físicos, procesos manuales de validación en la importación. Reducción de costos de impresión, almacenamiento y gestión. | Reducción de costos administrativos asociados a la documentación de importación  |
| Prima por Transparencia y Autenticidad | Capacidad de la empresa importadora de cobrar un precio superior por dispositivos con trazabilidad verificable (origen certificado, condiciones de transporte documentadas, autenticidad respaldada en blockchain), gracias a la reducción de la incertidumbre para el consumidor al momento de la compra.  | Incremento de margen de beneficio por diferenciación frente a la competencia  |
| Reducción de Fraudes y Falsificaciones | Inmutabilidad de registros en blockchain elimina posibilidad de falsificación de certificados y sustituciones de productos. Verificación mediante QR/NFC en Flutter. | Ahorro por reducción de fraudes |
| Menor Costo de Mantenimiento | La arquitectura moderna con FastAPI, Angular y Flutter facilita el mantenimiento y actualizaciones, reduciendo costos a largo plazo. | Reducción de costos de mantenimiento en un 30% |

# **CAPÍTULO. 1 MARCO TEÓRICO**

## **1.1. Marco Referencial** 

### **1.1.1. Fundamentos**

En la importación de dispositivos electrónicos de alta gama, la información generada durante la cadena de suministro adquiere un valor crítico para la confianza del consumidor final. Un dispositivo Apple recorre distintas etapas antes de llegar a manos del comprador boliviano: la compra al proveedor en EE.UU, el transporte internacional, el despacho aduanero, el almacenamiento, la distribución y, finalmente, la venta. En cada una de estas etapas participan actores distintos (proveedores, transportistas, autoridades aduaneras, importadoras y tiendas) que generan información relevante sobre el origen, las condiciones de transporte y la autenticidad del producto. Cuando esta información permanece fragmentada entre documentos físicos o sistemas internos no comunicados entre sí, el consumidor final no tiene forma de verificarla, lo que abre la puerta a la comercialización de dispositivos falsificados, robados o de origen irregular.

La trazabilidad de producto surge como respuesta a esta necesidad: permite reconstruir el recorrido completo de una unidad específica y responder, en cualquier punto de la cadena, a las preguntas de dónde proviene el dispositivo, qué eventos ha atravesado y quién ha sido responsable de cada uno. Para un proyecto centrado en dispositivos Apple, esta trazabilidad debe iniciar en el proveedor estadounidense y culminar en el consumidor final en Bolivia, identificando cada unidad individualmente mediante su número de serie, IMEI o EID.

Blockchain (específicamente la red Ethereum) aporta la capa de confianza necesaria para que esta información no pueda alterarse retrospectivamente. Sus propiedades de inmutabilidad, transparencia y auditabilidad permiten que, una vez registrado un evento crítico (por ejemplo, el despacho aduanero o la venta), ningún actor pueda modificarlo sin que la red lo detecte. Los smart contracts, desarrollados en Solidity, automatizan procesos como la verificación de autenticidad y la generación de certificados digitales, reduciendo la dependencia de procesos manuales.

Para conectar cada dispositivo físico con su historial digital, el sistema utiliza códigos QR (y, de forma complementaria, etiquetas NFC), generados automáticamente para cada unidad a partir de su identificador único. El consumidor escanea este código desde la aplicación móvil y accede al historial completo del dispositivo que está por comprar o que ya adquirió.

De esta manera, el sistema se fundamenta en la integración de cuatro elementos: la gestión empresarial de productos, órdenes de compra y unidades individuales; el registro de los eventos de la cadena de suministro internacional; el uso de blockchain para dotar de inmutabilidad a los registros críticos; y la identificación digital mediante código QR/NFC como puente entre el dispositivo físico y su información digital.

### **1.1.2. Generalidades**

La cadena de suministro del proyecto comprende el conjunto de actores, actividades y ubicaciones involucrados en llevar un dispositivo Apple desde su origen hasta el consumidor boliviano. A diferencia de una cadena de producción tradicional, aquí no existe un "productor" dentro del sistema: el punto de partida es la compra a un proveedor en Estados Unidos (actor externo sin cuenta), seguida por el transporte internacional, la intervención de la aduana boliviana, la recepción en almacén por parte de la empresa importadora, y finalmente la distribución y venta.

El sistema opera bajo una arquitectura multi-tenant: múltiples empresas importadoras y tiendas pueden utilizar la misma plataforma de forma aislada, manteniendo la independencia de sus datos y operaciones aunque compartan la infraestructura. Cada unidad de producto se identifica de forma individual —no por lote genérico, sino por su número de serie, IMEI o EID—, lo que permite un nivel de trazabilidad más preciso que el de sistemas orientados a lotes de producción masiva.

La información de trazabilidad puede exponerse, de forma secundaria, mediante una API REST documentada, permitiendo que plataformas externas de comercio electrónico consulten y muestren el historial de una unidad dentro de su propia ficha de producto, sin que el sistema gestione el proceso de compra ni el pago.

Asimismo, el sistema contempla el registro de incidencias durante el transporte o el almacenamiento (por ejemplo, condiciones de temperatura o vibración anómalas para baterías de litio), generando alertas dirigidas a los actores correspondientes, y permite construir indicadores y reportes sobre tiempos de importación, incidencias y cumplimiento normativo.

### **1.1.3. Características**

El sistema de información empresarial para la trazabilidad de productos presenta una serie de características que responden a las necesidades identificadas en la cadena de suministro y al objetivo de proporcionar información verificable al consumidor.

* **Trazabilidad de extremo a extremo**: representa el recorrido del dispositivo desde la compra en Estados Unidos hasta la entrega al consumidor final en Bolivia, relacionando cada evento de importación, transporte, aduana, almacenamiento y venta.  
* **Identificación individual de unidades**: cada dispositivo se identifica mediante su número de serie, IMEI o EID —no mediante lotes genéricos—, con un código QR o etiqueta NFC único generado automáticamente.  
* **Registro cronológico de eventos**: los eventos relevantes (compra, despacho aduanero, movimientos, venta, devolución) se registran en secuencia temporal, indicando fecha, actor responsable y ubicación.  
* **Control de acceso por roles**: seis actores con cuenta (Super Administrador, Administrador de Empresa, Gestor de Operaciones, Gestor de Ventas y Postventa, Consumidor Registrado, Auditor) acceden a funciones diferenciadas, además de actores externos sin cuenta y acceso público para verificación.  
* **Aislamiento multi-tenant**: los datos de cada empresa importadora permanecen aislados entre sí, aunque compartan la misma plataforma.  
* **Accesibilidad web y móvil**: El proyecto contempla una plataforma web (Angular) que atiende principalmente tareas administrativas y operativas, mientras que la aplicación móvil (Flutter) permite el escaneo de códigos y la consulta del historial en campo o por el consumidor. Esta característica permite adaptar el acceso al sistema a las necesidades de los diferentes actores.   
* **Verificación mediante código QR/NFC**: constituye el mecanismo de conexión entre el dispositivo físico y su historial digital, disponible incluso para visitantes sin cuenta.  
* **Registro inmutable en blockchain**: los eventos críticos se respaldan en la red Ethereum mediante smart contracts, garantizando que no puedan alterarse retrospectivamente.  
* **Certificados digitales de trazabilidad**: el sistema contempla generarlos automáticamente al momento de la venta, respaldados por los registros en blockchain, y pueden visualizarse o descargarse en PDF.  
* **Gestión de incidencias y alertas**: el sistema registra eventos anómalos durante el transporte o almacenamiento y notifica a los actores correspondientes.  
* **Generación de reportes**: permite analizar tiempos de importación, incidencias, ventas y cumplimiento normativo mediante indicadores exportables.

En conjunto, estas características permiten definir una solución que no se limita al almacenamiento de información, sino que busca representar y verificar el recorrido de los productos mediante un sistema integrado.

### **1.1.4. Conceptos específicos del rubro** 

* **Trazabilidad de producto**: Es la capacidad de seguir el historial, aplicación o localización de un producto mediante registros documentados. En el proyecto, la trazabilidad permite reconstruir el recorrido del producto (dispositivo móvil) desde su origen hasta el consumidor final.  
* **Cadena de suministro**: Es el conjunto de actores, actividades y ubicaciones involucrados en llevar el dispositivo desde el proveedor en Estados Unidos hasta el consumidor en Bolivia.  
* **Producto**: Es el bien que se registra dentro de la plataforma para ser producido, distribuido y comercializado.  
* **Unidad individual**: dispositivo físico específico, identificado de forma única mediante número de serie, IMEI o EID, sobre el cual se construye todo el historial de trazabilidad.  
* **Blockchain (Ethereum)**: Es una tecnología de registro distribuido, inmutable y descentralizado, utilizada para respaldar los eventos críticos de la cadena mediante smart contracts desarrollados en Solidity. Sus propiedades de inmutabilidad, transparencia, descentralización y auditabilidad hacen posible su utilización como soporte para determinados registros de trazabilidad.  
* **Smart contract**: programa auto-ejecutable almacenado en la blockchain, que automatiza procesos como la verificación de autenticidad y la emisión de certificados digitales.  
* **Identificador digital (QR/NFC)**: código o etiqueta que vincula el dispositivo físico con su información digital, generado automáticamente para cada unidad.  
* **Certificado digital de trazabilidad**: documento electrónico que resume el recorrido de una unidad, respaldado por los registros en blockchain, disponible para su consulta o descarga.  
* **Multi-tenant**: modelo de arquitectura que permite a múltiples empresas importadoras operar sobre la misma plataforma manteniendo sus datos completamente aislados entre sí.  
* **Administrador de Empresa**: usuario responsable de administrar el catálogo, los usuarios y las operaciones de su propia empresa (tenant) dentro de la plataforma.

## **1.2. Marco de trabajo ágil SCRUM**

### **1.2.1. Fundamentos de SCRUM**

SCRUM es un marco de trabajo ágil utilizado para desarrollar y gestionar productos complejos mediante ciclos iterativos e incrementales denominados Sprints. Su enfoque permite dividir un proyecto de gran dimensión en periodos de trabajo más pequeños, durante los cuales el equipo planifica, desarrolla, revisa y mejora una parte funcional del producto. Al finalizar cada Sprint, el equipo obtiene un incremento funcional que puede ser revisado para verificar si cumple con los requerimientos definidos. Esta característica es especialmente importante para nuestro proyecto, debido a que permite validar progresivamente el flujo completo de trazabilidad.

La metodología también permite identificar tempranamente dificultades técnicas. La integración entre una plataforma empresarial y blockchain puede presentar retos relacionados con el registro de transacciones, comunicación entre servicios y validación de información. Mediante iteraciones cortas, estos riesgos pueden ser identificados antes de que afecten al desarrollo completo del sistema.

Asimismo, SCRUM facilita la adaptación de los requerimientos. Durante el desarrollo pueden surgir nuevas necesidades relacionadas con los actores de la cadena de suministro, la forma de registrar eventos o la información que debe mostrarse al consumidor. La priorización del Product Backlog permite reorganizar el trabajo y adaptar los siguientes Sprints sin perder el control general del proyecto.

### **1.2.2. Roles en SCRUM**

* **Product Owner (PO):** Es el responsable de maximizar el valor del producto y administrar la priorización del Product Backlog. En el presente proyecto, este rol representa los intereses de los usuarios y stakeholders relacionados con la solución de trazabilidad. Su responsabilidad consiste en identificar y priorizar las funcionalidades más importantes para el sistema, considerando las necesidades de productores, distribuidores, consumidores y administradores. El Product Owner puede priorizar inicialmente funcionalidades esenciales como la gestión de usuarios, registro de productos, creación de lotes y trazabilidad, antes de funcionalidades complementarias como determinados reportes o integraciones adicionales. También participa en la validación de los incrementos desarrollados durante los Sprints.  
* **Scrum Master (SM):** Es responsable de facilitar la aplicación del marco de trabajo SCRUM y ayudar al equipo a eliminar impedimentos que afecten el desarrollo. En este proyecto, el Scrum Master coordina las actividades relacionadas con la planificación, Daily Scrum, Sprint Review y Sprint Retrospective, además de promover la comunicación y mejora continua del equipo. Entre sus responsabilidades también se encuentra facilitar la identificación de problemas que puedan afectar el desarrollo, como dificultades en la integración entre los componentes web, móvil, backend, base de datos o blockchain.  
* **Development Team:** Está conformado por los integrantes encargados de analizar, diseñar, desarrollar, integrar y probar el sistema. El equipo puede distribuir responsabilidades relacionadas con la plataforma web, aplicación móvil, backend, base de datos, seguridad, blockchain, pruebas y documentación.

  ### **1.2.3. Artefactos en SCRUM**

* **Product Backlog:** Es una lista priorizada de los requerimientos, funcionalidades y mejoras necesarias para desarrollar el sistema. En el proyecto de trazabilidad, el Product Backlog puede contener elementos relacionados con la gestión de usuarios, productos, lotes, códigos QR, eventos logísticos, blockchain, certificados, consulta del consumidor, notificaciones y reportes.  
* **Sprint Backlog:** Es el conjunto de elementos seleccionados del Product Backlog que serán desarrollados durante un Sprint determinado. Además de las funcionalidades seleccionadas, contiene las tareas necesarias para construir el incremento.  
* **Incremento:** Es la versión funcional del producto obtenida como resultado del trabajo realizado durante un Sprint. Cada incremento debe incorporar funcionalidades que hayan sido desarrolladas y verificadas.

  ### **1.2.4. Eventos en SCRUM**

* **Sprint:** Periodo de trabajo de duración determinada en el que el equipo desarrolla un conjunto de funcionalidades seleccionadas del Product Backlog. Durante cada Sprint se busca obtener un incremento funcional del sistema.

* **Sprint Planning:** Reunión inicial del Sprint en la que el equipo analiza y selecciona los elementos del Product Backlog que serán desarrollados, definiendo el objetivo del Sprint y las tareas necesarias para alcanzar dicho objetivo.

* **Daily Scrum:** Reunión breve y periódica del equipo de desarrollo en la que se revisa el progreso realizado, se identifican posibles impedimentos y se coordinan las actividades necesarias para cumplir el objetivo del Sprint.

* **Sprint Review:** Reunión realizada al finalizar el Sprint en la que se presenta el incremento desarrollado y se revisan las funcionalidades implementadas. Esta actividad permite verificar el cumplimiento de los requerimientos y obtener retroalimentación para futuras iteraciones.

* **Sprint Retrospective:** Reunión interna del equipo realizada después del Sprint Review, en la que se analiza el proceso de trabajo, identificando aspectos positivos, problemas encontrados y oportunidades de mejora para los siguientes Sprints.

  ### **1.2.5. Beneficios de SCRUM**

La aplicación de SCRUM proporciona diferentes beneficios para el desarrollo del sistema de información empresarial de trazabilidad.

* **Desarrollo incremental:** Permite construir el sistema progresivamente, comenzando por las funcionalidades esenciales y agregando posteriormente módulos más complejos. Esto facilita el control del alcance y permite obtener incrementos funcionales durante el desarrollo.  
* **Priorización de funcionalidades:** El Product Backlog permite ordenar las funcionalidades de acuerdo con su importancia para el proyecto. De esta manera, las capacidades esenciales de trazabilidad pueden desarrollarse antes que funcionalidades secundarias.  
* **Validación temprana:** Al finalizar cada Sprint se dispone de un incremento que puede ser revisado y probado. Esto permite detectar errores o problemas de diseño antes de que se acumulen durante las siguientes etapas.  
* **Adaptabilidad:** Los requerimientos pueden evolucionar a medida que el equipo comprende mejor las necesidades de los actores. SCRUM permite reorganizar el Product Backlog y adaptar el contenido de futuros Sprints.  
* **Trazabilidad del desarrollo:** SCRUM permite mantener una relación entre los requerimientos del sistema, las historias de usuario, tareas, incrementos y pruebas realizadas. 

# **CAPÍTULO 2\. Herramientas Tecnológicas Para El Desarrollo**

## **2.1. Lenguaje de Programación (WEB, MÓVIL)**

La selección de lenguajes de programación independientes y especializados permite desarrollar cada componente de la arquitectura utilizando tecnologías que se adaptan de manera óptima a sus necesidades específicas. Para este proyecto, el entorno de desarrollo se ha segmentado estratégicamente utilizando Python para la lógica del servidor, TypeScript para la construcción de la plataforma web y Dart para la aplicación móvil.

### **2.1.1. Web Frontend (Interfaz del Usuario)**

**TypeScript:** TypeScript es un lenguaje de programación avanzado desarrollado por Microsoft, el cual está basado en la sintaxis de JavaScript pero incorpora un sistema de tipado estático y herramientas modernas para el desarrollo de aplicaciones web complejas. A diferencia de JavaScript tradicional, TypeScript introduce mecanismos que permiten detectar errores de sintaxis y lógica de manera temprana durante la etapa de desarrollo. Esto se logra mediante la definición explícita de tipos de datos, lo que facilita la creación de sistemas informáticos más organizados, altamente escalables y más fáciles de mantener a lo largo del tiempo.

Dentro del alcance de este proyecto, TypeScript será utilizado en sinergia con el framework Angular para construir la plataforma web empresarial. Esta combinación tecnológica permitirá desarrollar interfaces de usuario robustas y dinámicas para los diferentes actores de la cadena de suministro, tales como fabricantes, distribuidores y administradores. Sus funciones principales abarcarán:

* Gestión y administración de usuarios y roles del sistema.  
* Registro detallado de productos electrónicos.  
* Interfaces para la consulta de información de trazabilidad.  
* Administración y seguimiento de eventos asociados al ciclo de vida del producto.  
* Generación y visualización de reportes analíticos del sistema.

### **2.1.2. Backend (Lógica del Servidor)**

**Python:** Python es un lenguaje de programación de alto nivel, interpretado y multiparadigma, ampliamente reconocido en la industria por su sintaxis clara, legible y la amplia disponibilidad de librerías especializadas. Su comprobada facilidad de integración con tecnologías web modernas, motores de bases de datos e incluso modelos de inteligencia artificial, lo convierte en una alternativa altamente adecuada para desarrollar aplicaciones de corte empresarial.

En el contexto de este proyecto, Python fungirá como el lenguaje principal del backend mediante la implementación del framework FastAPI. Este componente será el núcleo encargado de implementar la lógica empresarial, administrar el flujo de solicitudes provenientes del frontend (tanto web como móvil), comunicarse con la base de datos PostgreSQL y gestionar la integración asíncrona con la red Blockchain. Entre sus responsabilidades críticas estarán:

·        Gestión integral de los procesos de autenticación y autorización.  
·        Administración lógica del catálogo de productos.  
·        Registro y validación de los movimientos de trazabilidad de los artículos.  
·        Generación, exposición y consumo de servicios mediante API REST.  
·        Comunicación bidireccional segura con la red Hyperledger Fabric.

### **2.1.3. Móvil**

**Dart:** Dart es un lenguaje de programación orientado a objetos, de tipado seguro, desarrollado por Google y diseñado específicamente para construir aplicaciones multiplataforma de alto rendimiento. Su característica más destacada en el desarrollo moderno es su integración nativa y optimizada con el SDK Flutter, lo que permite desarrollar aplicaciones nativas tanto para sistemas operativos Android como iOS utilizando una única base de código.

Dentro de la arquitectura del proyecto, Dart será utilizado para crear la aplicación móvil dirigida al consumidor final. Mediante esta aplicación, el usuario podrá escanear códigos QR adheridos a los artículos y consultar, en tiempo real, información crítica relacionada con el origen, el recorrido logístico y la validación de autenticidad del producto.

## **2.2. Frameworks y entornos de ejecución**

Los frameworks seleccionados para esta arquitectura proporcionan estructuras de desarrollo estandarizadas que facilitan enormemente la construcción del sistema. El uso de estas herramientas reduce la complejidad técnica y permite implementar componentes modulares y reutilizables, optimizando los tiempos de desarrollo.

### **2.2.1. FastAPI**

**FastAPI** es un framework web moderno y de vanguardia basado en Python, diseñado específicamente para desarrollar servicios web y APIs REST de muy alto rendimiento. Se caracteriza por adoptar de forma nativa estándares abiertos de la industria como OpenAPI y JSON Schema. Esta estandarización permite generar documentación interactiva de forma automática y validar estrictamente la información recibida por los servicios web. Sus características principales incluyen:

* Alto rendimiento operativo mediante el uso de programación asíncrona.  
* Validación automática y serialización de datos de entrada y salida.  
* Generación de documentación interactiva de las APIs en tiempo real.  
* Fácil y segura integración con bases de datos y servicios de terceros externos.

Dentro del ecosistema del proyecto, FastAPI será el núcleo central del backend, actuando como el orquestador principal que comunicará las interfaces de Angular y Flutter con el almacenamiento en PostgreSQL y el registro inmutable en Hyperledger Fabric.

### **2.2.2. Angular**

**Angular** es un framework de desarrollo frontend basado en TypeScript, enfocado en el desarrollo de aplicaciones web de nivel empresarial (Single Page Applications) mediante una sólida arquitectura basada en componentes. 

Esta estructura modular permite a los equipos de desarrollo crear interfaces altamente organizadas, reutilizables y fácilmente escalables. En el marco de este proyecto, Angular será empleado para desarrollar la plataforma web administrativa, espacio donde las empresas involucradas en la cadena de suministro podrán registrar productos de manera segura, administrar información operativa y auditar la consulta de eventos de trazabilidad.

### **2.2.3. Flutter**

**Flutter** es un framework avanzado de Interfaz de Usuario (UI) desarrollado por Google para crear aplicaciones móviles multiplataforma de alta fidelidad. Utilizando Dart como su lenguaje principal de desarrollo, Flutter procesa su propio motor de renderizado, lo que le permite construir interfaces modernas, fluidas y con un rendimiento visual y operativo muy cercano al de las aplicaciones nativas.

En el contexto de la solución propuesta, Flutter será responsable de implementar:

* El módulo de lectura y procesamiento de códigos QR mediante la cámara del dispositivo.  
* La interfaz de consulta detallada del historial del producto.  
* La visualización amigable de la información de fabricación.  
* El punto de acceso principal del consumidor final al ecosistema de trazabilidad.

## **2.3. Sistema de gestor de base de datos**

**PostgreSQL:** PostgreSQL es un avanzado sistema gestor de bases de datos relacional (RDBMS) de código abierto, ampliamente reconocido en la industria del software por su excepcional estabilidad, robusta seguridad y estricto cumplimiento con los estándares del lenguaje SQL. Su arquitectura interna está diseñada para administrar grandes volúmenes de información, manteniendo en todo momento la integridad referencial y la consistencia de los datos bajo cargas transaccionales.

Dentro de la arquitectura híbrida del proyecto, PostgreSQL estará encargado de almacenar toda la información de carácter operativo, tal como:

- Credenciales y perfiles de usuarios.  
- Perfiles corporativos de las empresas participantes.  
- Catálogos de productos electrónicos.  
- Gestión de lotes de producción.  
- El historial de movimientos logísticos convencionales.  
- Los metadatos y datos descriptivos asociados a cada código QR.

Una de las características más importantes de este diseño es que PostgreSQL trabajará de manera complementaria junto con la red Blockchain. Mientras que la base de datos relacional administrará el grueso de la información operativa y descriptiva para garantizar tiempos de respuesta rápidos, Blockchain conservará exclusivamente los registros críticos y transacciones de valor que requieren una protección absoluta contra modificaciones no autorizadas.

## **2.4. Tecnología Blockchain**

**Ethereum** es una plataforma blockchain pública y descentralizada que permite no solo registrar transacciones, sino también ejecutar programas autónomos denominados smart contracts (contratos inteligentes) directamente sobre la red. A diferencia de una blockchain diseñada únicamente para transferencia de valor, Ethereum incorpora una máquina virtual (Ethereum Virtual Machine, EVM) capaz de procesar lógica programada, lo que permite automatizar reglas de negocio sin depender de un intermediario central.

Los contratos inteligentes en Ethereum se desarrollan mediante **Solidity**, un lenguaje de programación orientado a contratos, con una sintaxis similar a JavaScript. Su amplia adopción a nivel mundial se traduce en una extensa documentación, herramientas de desarrollo maduras y una comunidad activa, factores que facilitan su implementación en un proyecto académico con un equipo que se inicia en el desarrollo blockchain.

Dentro del sistema propuesto, Ethereum actuará como la capa de confianza encargada de registrar de manera inmutable los eventos críticos de la cadena de trazabilidad, entre ellos:

* La confirmación de la compra a proveedores en Estados Unidos.  
* El despacho aduanero en Bolivia.  
* Los movimientos logísticos relevantes de cada unidad.  
* La venta al consumidor final.

Cada uno de estos eventos generará un hash criptográfico y una marca de tiempo (timestamp) verificable, permitiendo que cualquier alteración posterior sea detectada por la red. Adicionalmente, los contratos inteligentes automatizarán procesos como la verificación de autenticidad del dispositivo (comparando el número de serie o IMEI con el registro almacenado) y la generación de certificados digitales de trazabilidad al momento de la venta.

Para la comunicación entre el backend y la red Ethereum, el sistema utilizará **Web3.py**, una librería de Python que permite enviar transacciones, invocar funciones de los contratos inteligentes y consultar el estado de la blockchain desde la API desarrollada en FastAPI.

Durante la fase de desarrollo y pruebas, el sistema se desplegará sobre una **red de prueba (testnet)** de Ethereum, como **Sepolia** o **Amoy**, las cuales replican el funcionamiento de la red principal sin costo real, mediante criptomonedas de prueba obtenidas a través de "grifos" (faucets). Esto permite validar el flujo completo de registro y verificación de eventos sin necesidad de operar sobre la red principal (mainnet), cuyo uso implica costos reales por transacción (gas fees).

Sus características técnicas relevantes para el proyecto son:

* Inmutabilidad de los registros una vez confirmados en la red.  
* Ejecución automática y verificable de reglas de negocio mediante smart contracts.  
* Transparencia y auditabilidad de los eventos registrados.  
* Amplio soporte de herramientas de desarrollo (Solidity, Web3.py, testnets gratuitas) adecuado para un entorno académico.

## **2.5. Código QR como Mecanismo de Identificación**

Los códigos QR (Quick Response) actuarán como el puente tecnológico y vínculo físico entre el producto material y su representación digital en la plataforma. Para garantizar un seguimiento exacto, cada producto electrónico manufacturado poseerá un identificador único (ID) que estará directamente asociado a un código QR impreso o adherido al mismo.

El flujo operativo y de funcionamiento se define de la siguiente manera:

1\.  	La empresa fabricante registra el producto en la plataforma web.  
2\.  	El sistema genera automáticamente un código QR único y seguro.  
3\.  	El consumidor final utiliza la aplicación desarrollada en Flutter para escanear dicho código.  
4\.  	El backend procesa la petición y consulta la información consolidada.  
5\.  	La aplicación móvil despliega en pantalla el historial almacenado y validado del producto.

La implementación de esta tecnología facilita una consulta rápida, intuitiva y accesible, mejorando de manera sustancial la confianza del consumidor hacia la marca y el producto adquirido.

## **2.6. Lenguaje de modelado de software (Modelo C4)**

Para documentar y estructurar el diseño del sistema, se empleará el Modelo C4, una técnica de ingeniería de software utilizada para representar la arquitectura de sistemas informáticos mediante diferentes niveles de abstracción estandarizados. Esta metodología asegura que todos los involucrados comprendan la plataforma desde diferentes perspectivas técnicas:

* **Nivel 1 \- Contexto del sistema:** Representa a alto nivel la relación y las interacciones entre los actores principales (fabricantes, distribuidores, consumidores) y el sistema de trazabilidad en su conjunto.  
* **Nivel 2 \- Contenedores:** Detalla las responsabilidades de los principales componentes tecnológicos ejecutables, tales como:

  * La Aplicación web construida en Angular.  
  * La Aplicación móvil desarrollada en Flutter.  
  * El servicio Backend gestionado por FastAPI.  
  * El motor de base de datos PostgreSQL.  
  * Los nodos de la red Hyperledger Fabric.  
* **Nivel 3 \- Componentes:** Describe a un nivel más granular los módulos lógicos internos dentro de un contenedor específico, desglosando áreas funcionales como:  
  * Módulos de seguridad y autenticación.  
  * Lógica de gestión de productos.  
  * Reglas de negocio de trazabilidad.  
  * Adaptadores de integración Blockchain.  
  * Motor de generación de reportes.

## **2.7. Herramienta de diseño y modelado (Enterprise Architect)**

**Enterprise Architect:** Es una herramienta profesional de modelado UML desarrollada por Sparx Systems, que permite a arquitectos y desarrolladores crear, visualizar y documentar modelos complejos de software. Ofrece funcionalidades avanzadas como ingeniería inversa (generar diagramas desde código existente), ingeniería directa (generar código desde modelos), simulación de comportamientos y generación automática de documentación. Soporta múltiples estándares como UML, SysML, BPMN y ArchiMate. Aunque su costo y curva de aprendizaje pueden ser elevados para proyectos académicos, es una opción valiosa para entornos empresariales donde se requiere un control riguroso de la arquitectura y trazabilidad entre el diseño y la implementación.

## **2.8. Entorno de Desarrollo**

Para la construcción y codificación del software, **Visual Studio Code** será adoptado como el entorno principal de desarrollo integrado (IDE). Esta decisión se fundamenta en su alta flexibilidad, ligereza y excelente compatibilidad nativa con los lenguajes y frameworks del proyecto: Python, Angular y Flutter, así como su robusta integración con herramientas de control de versiones.

Como complemento a la escritura de código, el ciclo de desarrollo se apoyará en:

* **Postman:** Para el diseño, prueba y validación de los endpoints de las APIs REST.  
* **Flutter SDK:** Conjunto de herramientas necesario para la compilación del entorno de desarrollo móvil.  
* **Angular CLI:** Interfaz de línea de comandos indispensable para la construcción y andamiaje del frontend web.  
* **Herramientas de administración PostgreSQL:** Para la conexión, visualización y gestión visual de las bases de datos relacionales.

## **2.9. Infraestructura de software (IaaS)**

### **2.9.1. Servicio en la nube (Cloud Computing)**

El Cloud Computing es un modelo tecnológico que permite acceder a servicios informáticos a través de internet sin necesidad de administrar directamente servidores físicos.

Estos servicios pueden incluir:

* Servidores virtuales.  
* Bases de datos.  
* Almacenamiento.  
* Redes.  
* Herramientas de desarrollo.  
* Servicios de seguridad.

Una de las principales ventajas del uso de computación en la nube es que permite a los sistemas adaptarse a diferentes niveles de demanda, evitando inversiones elevadas en infraestructura física.

Dentro del proyecto se utilizarán servicios Cloud para mantener disponible la plataforma web, la API del sistema y los servicios asociados a la gestión de información.

### **2.9.2. (Azure, Amazon AWS, IBM Cloud, Google Cloud, otros)**

**Google Cloud Platform (GCP)** es la plataforma de servicios de computación en la nube desarrollada por Google, que permite acceder a infraestructura virtualizada (servidores, bases de datos, almacenamiento y redes) a través de internet, sin necesidad de administrar directamente equipos físicos. Su modelo de pago por uso permite escalar los recursos según la demanda real del sistema, evitando inversiones iniciales elevadas en infraestructura propia.

Dentro del proyecto, GCP será la plataforma utilizada para el despliegue completo del sistema, tanto en su fase de desarrollo como en la puesta en marcha final para la defensa. Sus servicios permitirán alojar el backend, la base de datos, el almacenamiento de archivos y la distribución de contenido estático de la plataforma. Los componentes principales contemplados son:

* **Compute Engine**, para alojar el backend desarrollado en FastAPI, con posibilidad de autoescalado y balanceo de carga según el volumen de solicitudes.  
* **Cloud SQL para PostgreSQL**, como servicio de base de datos gestionado, con copias de respaldo automáticas y alta disponibilidad.  
* **Cloud Storage**, para el almacenamiento de imágenes, documentos y certificados digitales generados por el sistema.  
* **Cloud CDN**, para la entrega de archivos estáticos (imágenes, CSS, JS) con baja latencia a los usuarios de la plataforma web.  
* **Cloud Monitoring y Cloud Logging**, para la supervisión del rendimiento, la disponibilidad y el registro de actividad de la infraestructura.  
* **Docker**, para empaquetar los servicios de la aplicación y facilitar su despliegue portable dentro de GCP.

El uso de una plataforma unificada para el desarrollo y la puesta en marcha permite al equipo mantener consistencia entre el entorno de pruebas y el entorno de defensa final, reduciendo el riesgo de comportamientos distintos entre ambos escenarios y facilitando la administración de la infraestructura a lo largo del proyecto.

### **2.9.3. SAAS (Software as a Service, SaaS)**

**SaaS (*Software as a Service*)** es un modelo de distribución de software donde las aplicaciones son proporcionadas mediante internet, permitiendo que los usuarios accedan a ellas sin necesidad de instalar programas localmente.

En este modelo, el proveedor se encarga de:

* Mantenimiento del software.  
* Actualizaciones.  
* Seguridad.  
* Disponibilidad del servicio.

Entre sus principales ventajas se encuentran:

* Acceso desde cualquier dispositivo con conexión a internet.  
* Reducción de costos de infraestructura.  
* Actualizaciones automáticas.  
* Facilidad de colaboración entre usuarios.

Dentro del proyecto, algunos servicios externos pueden funcionar bajo este modelo, como:

* Plataformas de gestión del proyecto.  
* Herramientas colaborativas.  
* Servicios de almacenamiento.  
* Servicios complementarios utilizados durante el desarrollo.

## **2.10. Herramientas Colaborativas para Seguimientos de Proyectos (Jira Software, Trello, Confluence, otros)**

Para la gestión ágil del proyecto bajo el marco de trabajo SCRUM, el equipo utilizará un ecosistema de herramientas en la nube que permitirá la sincronización.

* **Trello / Jira Software:** Se utilizará como el tablero principal para gestionar el Product Backlog.

Historias de Usuario: Cada requerimiento funcional ,desde el RF1 hasta el RF49, se transformará en una tarjeta o Historia de Usuario bajo el formato "Como/Quiero/Para".  
Gestión de Sprints: Se emplearán tableros Kanban para organizar el trabajo en los 4 Sprints definidos en el cronograma. Las columnas permitirán visualizar en tiempo real qué tareas están Pendientes, En Proceso y Finalizadas.  
Estimación vs. Ejecución: La herramienta permitirá registrar la estimación de horas por cada tarea y compararla con el tiempo de ejecución real para generar el gráfico Burn-down del equipo.

* **Confluence:** Se empleará como la base de conocimientos centralizada y el repositorio de documentación técnica del proyecto.

Documentos Técnicos: Aquí se alojarán el Diccionario de Datos, los diagramas de arquitectura del Modelo C4, y la documentación detallada de la API REST.  
Manuales y Bitácoras: Servirá para centralizar los Manuales de Usuario y la bitácora de cambios de la plataforma, asegurando que tanto el entorno Web como el Móvil mantengan coherencia técnica.

## **2.11. Sistema de control de Versiones de código (Git)**

**Git** es un sistema de control de versiones distribuido que permite registrar y gestionar los cambios realizados sobre el código fuente de un proyecto. Su naturaleza distribuida permite que cada integrante del equipo mantenga una copia completa del historial del proyecto, facilitando el trabajo en paralelo mediante ramas independientes, la fusión de cambios y la recuperación de versiones anteriores sin depender de un servidor central.

Dentro del proyecto, Git permitirá organizar el desarrollo del backend (FastAPI), la plataforma web (Angular), la aplicación móvil (Flutter) y los smart contracts (Solidity) mediante un flujo de trabajo basado en ramas por funcionalidad (*feature branching*), con commits descriptivos que documenten cada cambio realizado. Esto garantiza trazabilidad sobre el propio desarrollo del sistema: qué se modificó, cuándo y por quién.

El equipo utilizará GitHub como plataforma remota para alojar los repositorios, gestionar *pull requests* y realizar revisiones de código antes de integrar cambios a la rama principal, además de su integración con herramientas de gestión de proyecto como Jira para vincular tareas con commits.

## **2.12. Herramientas de Gestión de Código en la Nube (Bitbucket)**

**Bitbucket**

Bitbucket es una plataforma de alojamiento y colaboración para proyectos de software basada en Git. Permite almacenar repositorios de código en la nube y facilita el trabajo en equipo. Ofrece herramientas para administrar repositorios, ramas, commits y pull requests, manteniendo un control organizado de las versiones del código.

En un proyecto colaborativo, cada integrante puede trabajar en una rama independiente sin afectar la línea principal. Una vez terminado el cambio, se envía al repositorio remoto y se revisa mediante un pull request antes de integrarlo. Esto facilita la revisión del código, la detección de errores y el control de los cambios.

Entre sus principales características están la administración de repositorios Git, gestión de ramas, registro de commits, comparación de cambios, pull requests, revisión colaborativa y restricciones sobre ramas. Estas funciones ayudan a mantener una estructura de trabajo controlada y reducen el riesgo de que cambios no revisados afecten el código principal.

Se considera como alternativa a GitHub para centralizar los componentes de backend, frontend web y aplicación móvil, especialmente por su integración nativa con otras herramientas de Atlassian, como Jira, lo que permite relacionar directamente la planificación de tareas con las ramas y commits correspondientes, facilitando el seguimiento desde la planificación hasta la implementación del código. 

# **CAPÍTULO 3\. REQUERIMIENTOS**

## **3.1. Propósito**

El propósito de este documento de requisitos es definir y describir de manera detallada las necesidades, funcionalidades y restricciones del Sistema de Información Empresarial para Plataforma y Aplicación Móvil con Blockchain para la Trazabilidad de Dispositivos Apple Importados.

Este capítulo establece la base para el desarrollo del sistema, sirviendo como guía para el equipo de desarrollo, el Product Owner y los stakeholders. Los requisitos aquí documentados permitirán:

* Alinear las expectativas de los actores involucrados: Super Administrador, Administrador de Empresa, Gestor de Operaciones, Gestor de Ventas y Postventa, Consumidor Registrado y Auditor/Inspector Externo.  
* Establecer un alcance claro del sistema, definiendo qué funcionalidades se desarrollarán y cuáles quedan fuera del proyecto durante el semestre.  
* Facilitar la planificación de los Sprints, priorizando las funcionalidades más críticas para la trazabilidad blockchain.  
* Servir como base para las pruebas de aceptación y validación del sistema.  
* Garantizar la trazabilidad de cada dispositivo desde su compra en Estados Unidos hasta su entrega al consumidor final en Bolivia, cumpliendo con los objetivos generales y específicos del proyecto.

El sistema busca proporcionar una solución integral que permita:

* Registrar unidades individuales de productos Apple (por número de serie, IMEI o EID) y los eventos de su cadena de suministro.  
* Almacenar de manera inmutable los eventos críticos de trazabilidad mediante tecnología blockchain.  
* Permitir que el consumidor y el público en general consulten el historial completo de un dispositivo mediante su código QR o etiqueta NFC.  
* Automatizar procesos de verificación de autenticidad, generación de certificados digitales y alertas mediante smart contracts.  
* Operar bajo una arquitectura multi empresa (multi-tenant) que permita a distintas importadoras utilizar la plataforma de forma aislada y segura.

## **3.2. Ámbito de Sistema**

El Sistema de Información Empresarial para Trazabilidad Blockchain abarca el desarrollo de una plataforma web y una aplicación móvil integradas, que cubren el recorrido completo de un dispositivo Apple importado, desde su compra en EE.UU. hasta su entrega al consumidor final en Bolivia. El ámbito del sistema se delimita en los siguientes dominios: 

### **3.2.1 Dominio Funcional**

| Área | Descripción |
| ----- | ----- |
| **Gestión de Usuarios y Seguridad** | Administración de cuentas, roles y permisos de los seis actores del sistema, bajo un modelo multi-tenant que garantiza el aislamiento de datos entre empresas participantes. |
| **Catálogo y Certificaciones de Productos** | Registro y administración de los productos Apple comercializados por cada empresa, junto con las certificaciones técnicas y de garantía que respaldan su autenticidad. |
| **Abastecimiento, Actores y Logística de Importación** | Gestión de órdenes de compra a proveedores en Estados Unidos, recepción de mercancía tras el despacho aduanero, y registro de los participantes externos y ubicaciones físicas involucrados en el proceso. |
| **Inventario y Trazabilidad (núcleo)** | Identificación individual de cada dispositivo mediante número de serie, IMEI o EID, y seguimiento de su recorrido completo —desde la importación hasta la entrega al consumidor— incluyendo la verificación de autenticidad. |
| **Comercialización (Ventas y Postventa)** | Registro del evento de venta de cada unidad al consumidor final y gestión posterior de devoluciones, garantías y documentación asociada. |
| **Blockchain e Integridad de Datos** | Registro descentralizado e inmutable de los eventos críticos de la cadena de trazabilidad, y generación de certificados digitales verificables respaldados en dichos registros. |
| **Consulta y Reportes** | Acceso del consumidor al historial de sus productos mediante web o app móvil, y generación de indicadores y reportes de trazabilidad para las empresas y el Super Administrador. |

### **3.2.2. Dominio Técnico**

| Área | Descripción |
| :---- | :---- |
| **Arquitectura** | Aplicación basada en API REST (FastAPI), frontend web (Angular), aplicación móvil (Flutter) y base de datos relacional (PostgreSQL), bajo un modelo multi-tenant.  |
| **Blockchain** | Integración con la red blockchain Ethereum mediante smart contracts desarrollados en Solidity, para el registro inmutable de eventos críticos de trazabilidad.  |
| **Infraestructura** | Despliegue en la nube sobre Google Cloud Platform (GCP), con autoescalado, balanceo de carga, alta disponibilidad y recuperación ante desastres.  |
| **Seguridad** | Autenticación mediante JWT/OAuth2, cifrado de datos en tránsito (HTTPS) y en reposo, gestión segura de claves criptográficas (HSM). |
| **Identificación Digital** | Generación de códigos QR únicos por unidad, lectura mediante cámara del dispositivo móvil (Flutter) y registro de consultas de trazabilidad. |

### **3.2.3. Plataformas comprendidas**

* **Plataforma web:** utilizada principalmente por el Super Administrador, el Administrador de Empresa, el Gestor de Operaciones y el Gestor de Ventas y Postventa para las tareas administrativas y operativas.  
* **Aplicación móvil:** utilizada principalmente por el Consumidor Registrado y por el Gestor de Operaciones para el escaneo de códigos QR/NFC y la consulta o registro de eventos en campo.  
* **Backend y red blockchain:** componentes de soporte, sin interfaz directa para el usuario final, encargados de procesar la lógica de negocio y garantizar la inmutabilidad de los registros.

  ### **3.2.4. Usuarios Del Sistema**

| Rol | Tipo de acceso | Descripción general |
| ----- | ----- | ----- |
| **Super Administrador** | Con cuenta | Control total de la plataforma; único rol que puede crear y eliminar empresas. |
| **Administrador de Empresa** | Con cuenta | Responsable de una empresa (tenant); gestiona catálogo, usuarios y aprueba compras. |
| **Gestor de Operaciones** | Con cuenta | Gestiona abastecimiento, inventario y logística de las unidades. |
| **Gestor de Ventas y Postventa** | Con cuenta | Gestiona ventas, devoluciones y garantías. |
| **Consumidor Registrado** | Con cuenta | Adquiere productos y consulta su historial de trazabilidad. |
| **Auditor / Inspector Externo** | Con cuenta | Verifica el cumplimiento normativo y la integridad de la cadena, con acceso de solo lectura. |
| **Proveedor EE.UU., Transportista Internacional, Aduana**  | Sin cuenta  | Participantes externos referenciados en los eventos de trazabilidad.  |
| **Visitante Anónimo**  | Sin cuenta  | Cualquier persona que escanea un código QR y consulta el historial público del producto.  |

## **3.3. Equipo SCRUM**

## **3.4. Definiciones, Acrónimos y Abreviaturas (Referencias)**

## **3.5. Funciones del Producto (Describir características de funcionalidad)**

El sistema de trazabilidad blockchain incluye las siguientes funciones principales, organizadas por módulos y actores:

### **Módulo de Seguridad y Multi-Tenant**

| Función | Descripción | Actor |
| ----- | ----- | ----- |
| **Gestión de Empresas (Tenants)** | Creación, configuración, suspensión y eliminación de empresas que operan sobre la plataforma, garantizando el aislamiento de datos entre cada una. | Super Administrador |
| **Gestión de Usuarios por Empresa** | Creación, edición y desactivación de cuentas de usuario dentro de una empresa específica, asignando roles y permisos según responsabilidad. | Administrador de Empresa |
| **Asignación de Roles** | Asignación de roles a usuarios dentro de su empresa (Gestor de Operaciones, Gestor de Ventas y Postventa, Auditor, etc.). | Administrador de Empresa |
| **Consulta de Bitácora** | Visualización de registros de auditoría por parte del Super Administrador (a nivel global) y del Auditor (con fines de cumplimiento normativo). | Super Administrador, Auditor |

### **Módulo de Catálogo y Certificaciones** 

| Función | Descripción | Actor |
| ----- | ----- | ----- |
| **Registro de Producto** | Creación de nuevo producto con información detallada: nombre, descripción, categoría, origen (georreferenciación), fecha de producción, ingredientes/materiales, atributos diferenciadores y certificaciones. | Administrador de empresa |
| **Edición de Producto** | Modificación de información del producto (con registro de auditoría de cambios). | Administrador de empresa |
| **Desactivación del Producto** | Desactivación lógica de producto (no se elimina físicamente para mantener historial). | Administrador de empresa |
| **Listado de Productos** | Visualización de todos los productos registrados por el productor, con filtros por categoría, fecha y estado. | Administrador de Empresa, Gestor de Operaciones, Gestor de Ventas y Postventa |
| **Detalle de Producto** | Consulta de información completa de un producto específico, incluyendo lotes asociados y eventos de trazabilidad. | Administrador de Empresa, Gestor de Operaciones, Gestor de Ventas y Postventa, Consumidor Registrado |
| **Gestion de categorías**  | Creación, edición y organización de categorías de productos (Smartphones, Laptops, Tablets, Audífonos, Accesorios) | Super Administrador, Administrador de Empresa |
| **Gestión de Certificaciones** | Asociación de certificaciones técnicas (FCC, CE, RoHS, Energy Star, garantía internacional del fabricante) a cada producto del catálogo, y visualización en su ficha. | Administrador de Empresa |

### **Módulo de abastecimiento e importacion**

| Función | Descripción | Actor |
| ----- | ----- | ----- |
| **Registro de Compra** | Creación de órdenes de compra a proveedores en Estados Unidos, con número de orden, proveedor, fecha y total en USD. | Gestor de Operaciones |
| **Detalle de Compra** | Registro de productos comprados (variante, cantidad, costo unitario y subtotal). | Gestor de Operaciones |
| **Aprobación de Compra** | Flujo de aprobación de órdenes de compra por parte del Administrador de Empresa. | Administrador de Empresa |
| **Registro de Recepción** | Registro de la recepción física de mercancía en Bolivia, asociada a una compra, con ubicación, número de documento y estado. | número de documento y estado.	Gestor de Operaciones |
| **Detalle de Recepción** | Registro de cantidades esperadas vs. cantidades recibidas por producto (para gestionar faltantes o sobrantes). | Gestor de Operaciones |
| **Generación de Unidades** | Visualización del estado de las órdenes de compra en curso (pendiente, enviada, recibida\_parcial, recibida\_total, cancelada). | Administrador de Empresa, Gestor de Operaciones |

### **Módulo de Actores y Ubicaciones** 

| Función | Descripción | Actor |
| ----- | ----- | ----- |
| **Registro de Actor Externo** | Creación y administración de participantes externos de la cadena de suministro: Proveedor en EE.UU., Transportista Internacional y Aduana. | Administrador de Empresa |
| **Registro de Ubicación** | Creación y administración de ubicaciones físicas (almacenes, puertos de entrada, oficinas aduaneras, tiendas) con georreferenciación. | Administrador de Empresa |
| **Asociación Actor-Ubicación** | Vinculación de ubicaciones a actores (un actor puede tener múltiples ubicaciones). | Administrador de Empresa |
| **Consulta de Actores y Ubicaciones** | Visualización de la lista de actores y ubicaciones registradas, con filtros por tipo y ciudad. | Administrador de Empresa, Gestor de Operaciones,  |

### **Módulo de Inventario y Trazabilidad  — Núcleo del Sistema**

| Función | Descripción | Actor |
| ----- | ----- | ----- |
| **Registro de Unidad Individual** | Registro de cada dispositivo físico con su número de serie único, IMEI (para dispositivos móviles), EID, UUID público, estado, ubicación actual y custodio actual. | Gestor de Operaciones |
| **Generación de Código QR** | Generación automática de un código QR único por unidad, con token público y URL de consulta | Gestor de Operaciones |
| **Impresión de Código QR** | Descarga e impresión de códigos QR para etiquetado físico de los dispositivos. | Gestor de Operaciones |
| **Registro de Envío** | Creación de traslados logísticos entre ubicaciones (origen, destino, transportista, fechas, tracking externo). |  Gestor de Operaciones |
| **Asignación de Unidades a Envío** | Asignación de unidades específicas (por serial/IMEI) a un envío, permitiendo que un envío transporte múltiples unidades. | Gestor de Operaciones |
| **Registro de Evento de Trazabilidad** | Registro de acciones relevantes: fabricación, exportación, llegada a puerto, despacho aduanero, recepción, traslado, venta, devolución. Cada evento registra fecha, actores, ubicación y descripción. | Gestor de Operaciones |
| **Registro de Condiciones de Transporte** | Registro de temperatura, humedad, presión y nivel de vibración durante los traslados (crítico para dispositivos con baterías de litio), de forma manual o mediante integración con sensores IoT. | Gestor de Operaciones |
| **Escaneo de Código QR/NFC** | Lectura del código QR o etiqueta NFC desde la aplicación móvil para consultar el historial del dispositivo, tanto por el Gestor de Operaciones (para registrar eventos) como por el Consumidor. | Gestor de Operaciones, Consumidor Registrado, Visitante Anónimo |
| **Registro de Consulta de Trazabilidad** | Registro de cada escaneo del QR (fecha, IP, ubicación aproximada, user agent) para auditar el interés del consumidor. | Sistema (automático) |
| **Generación de Alerta Automática** | Generación de alertas ante condiciones anómalas (temperatura extrema, vibraciones excesivas, retrasos aduaneros, inconsistencias en la cadena). | Sistema (automático) |
| **Consulta de Historial de Trazabilidad** | Visualización del historial cronológico completo de una unidad, desde la compra en EE.UU. hasta la venta al consumidor, con mapa interactivo del recorrido. | Consumidor Registrado, Visitante Anónimo, Auditor |
| **Verificación de Autenticidad** | Confirmación de que el dispositivo es original y no ha sido falsificado, mediante validación de registros en blockchain. | Consumidor Registrado, Visitante Anónimo |
| **Reporte de Sospecha** | Función para reportar un dispositivo sospechoso de falsificación o irregularidad, registrando la denuncia junto con la evidencia proporcionada. | Consumidor Registrado, Visitante Anónimo |
| **Gestión de Alertas** | Visualización, clasificación y resolución de alertas generadas por el sistema (pendiente, en\_proceso, resuelta). | Gestor de Operaciones, Administrador de Empresa |

### **Módulo de Integración con Blockchain**

| Función | Descripción | Actor |
| ----- | ----- | ----- |
| **Registro en Blockchain** | Almacenamiento inmutable de eventos críticos de trazabilidad (compra, despacho aduanero, movimientos, entrega, venta) en la red blockchain. | Sistema (Backend \+ Smart Contract) |
| **Generación de Hash y Timestamp** | Creación de hash criptográfico de cada evento y marca de tiempo verificable, asociados a la transacción en blockchain. | Sistema (Backend) |
| **Confirmación Visual al Usuario** | Confirmación visual al usuario del envío del evento a blockchain, mostrando estado "pendiente" hasta su confirmación en red (latencia \< 2 segundos) | Sistema (Backend) |
| **Verificación de Integridad** | Comparación de registros locales con los almacenados en blockchain para detectar alteraciones. | Auditor, Super Administrador |
| **Consulta de registros Blockchain** | Acceso a la información almacenada en blockchain para verificar la integridad de los registros y compararlos con los datos operativos. | Auditor, Super Administrador |
| **Generación de Certificado Digital** | Generación automática de certificado digital de trazabilidad para cada unidad al momento de su venta, respaldado por los registros almacenados en blockchain. | Sistema (Backend) |
| **Visualización y Descarga de Certificado** | Visualización y descarga en formato PDF del certificado digital de trazabilidad de una unidad. | Consumidor Registrado, Visitante Anónimo |
| **Generación de Reportes** | Generación de reportes e indicadores de trazabilidad (tiempos de importación, incidencias, ventas, cumplimiento normativo) con filtros por período y exportación de datos. | Administrador de Empresa, Super Administrador |

### **Módulo de Ventas**

| Función | Descripción | Actor |
| ----- | ----- | ----- |
| **Registro de Venta** | Registro del evento de venta de una unidad específica al consumidor final (fecha, empresa vendedora, canal de venta, total). | Gestor de Ventas y Postventa |
| **Detalle de Venta** | Registro de productos/variantes vendidos, cantidades, precios unitarios y subtotales. | Gestor de Ventas y Postventa |
| **Asignación de Unidades a Venta** | Asignación de unidades físicas (por serial/IMEI) a cada línea de venta, garantizando que se sepa exactamente qué dispositivo fue vendido en cada transacción. | Gestor de Ventas y Postventa |
| **Registro de Pago** | Registro de pagos asociados a una venta (método de pago, monto, fecha, estado). | Gestor de Ventas y Postventa |
| **Actualización de Estado de Unidad** | Actualización automática del estado de la unidad a "vendido" y asignación del consumidor como custodio actual. | Sistema (automático) |
| **Consulta de Historial de Ventas** | Visualización del historial de ventas de la empresa, con filtros por fecha, cliente y producto. | Gestor de Ventas y Postventa, Administrador de Empresa |

### **Módulo de Postventa**

| Función | Descripción | Actor |
| ----- | ----- | ----- |
| **Registro de Devolución** | Registro de devoluciones asociadas a una venta, con motivo, descripción y estado (solicitada, aprobada, rechazada, procesada). | Gestor de Ventas y Postventa |
| **Asignación de Unidades a Devolución** | Relación N:M entre devoluciones y unidades (una devolución puede incluir varios dispositivos). | Gestor de Ventas y Postventa |
| **Registro de Garantía por Unidad** | Registro de fechas de inicio y fin de garantía, proveedor de la garantía y condiciones específicas. | Gestor de Ventas y Postventa |
| **Adjunto de Documentos** | Subida y almacenamiento de documentos adjuntos por unidad: facturas, certificados de importación, comprobantes de garantía, certificados de autenticidad, con hash del archivo para verificar su integridad. | Gestor de Ventas y Postventa |
| **Consulta de Garantía** | Visualización del estado de garantía de una unidad específica por parte del consumidor. | Consumidor Registrado |
| **Consulta de Historial de Compras** | Visualización del historial de compras y unidades adquiridas por el consumidor. | Consumidor Registrado |
| **Guardado de Favoritos** | Función para guardar productos o lotes como favoritos y recibir notificaciones sobre incidencias o retiros relacionados con sus unidades. | Consumidor Registrado |

## **3.6. Product Backlog**

**SPRINT 0 – Arquitectura, empresas, usuarios y roles**

**Objetivo**: se establecerán las bases del proyecto, definiendo la arquitectura general, modelo de datos, estructura de los componentes web y móvil, establecer la base técnica del sistema e implementar los tres primeros casos de uso: gestión de empresas, usuarios y asignación de roles y permisos.

| SPRINT 0 |  |  |  |  |  |
| ----- | :---- | :---- | :---- | :---- | :---- |
| **ID** | **ROL** | **Características / Funcionalidad** | **Prioridad** | **Tiempo estimado** | **Plataforma** |
| T001 | Development Team (Arquitectura) | Definición de la arquitectura general del sistema | Alta | 5h | Arquitectura |
| T002 | Development Team (Backend) | Configuración inicial del proyecto Backend con FastAPI | Alta | 4h | Backend |
| T003 | Development Team (Frontend) | Configuración inicial de la plataforma Web con Angular | Alta | 4h | Web |
| T004 | Development Team (Mobile) | Configuración inicial de la aplicación Móvil con Flutter | Alta | 4h | Móvil |
| T005 | Development Team (Backend) | Configuración de la conexión con PostgreSQL | Alta | 4h | Backend |
| T006 | Development Team (Backend) | Diseño del modelo de datos para empresas, usuarios, roles y productos | Alta | 5h | Base de Datos |
| T007 | Development Team (Backend) | Definición de entidades y relaciones principales del sistema | Alta | 4h | Base de Datos |
| T008 | Development Team (Backend) | Implementación de gestión de empresas y configuración multiempresa (API REST) | Alta | 5h | Backend |
| T009 | Development Team (Frontend) | Interfaz de gestión de empresas (UI Angular) | Alta | 4h | Web |
| T010 | Development Team (Backend) | Implementación de gestión de usuarios del sistema (API REST) | Alta | 5h | Backend |
| T011 | Development Team (Frontend) | Interfaz de administración de usuarios (UI Angular) | Alta | 4h | Web |
| T012 | Development Team (Backend) | Implementación de roles y permisos de usuarios (RBAC) | Alta | 5h | Backend |
| T013 | Development Team (Frontend) | Interfaz de asignación de roles y permisos (UI Angular) | Alta | 4h | Web |

 

**Casos de uso cubiertos**

* **CU-001:** Gestionar Empresas  
* **CU-002:** Gestionar Usuarios del Sistema  
* **CU-003:** Asignar Roles y Permisos a Usuario

**SPRINT 1 – Autenticación y gestión de productos**

**Objetivo:** completar la seguridad de acceso y desarrollar la estructura principal de productos, variantes, categorías, certificaciones, catálogo, actores y ubicaciones.

| SPRINT 1 |  |  |  |  |  |
| ----- | :---- | :---- | :---- | :---- | :---- |
| **ID** | **ROL** | **Características / Funcionalidad** | **Prioridad** | **Tiempo estimado** | **Plataforma** |
| T014 | Development Team (Backend) | Implementación de autenticación y recuperación de contraseña (JWT \+ OAuth2) | Alta | 5h | Backend |
| T015 | Development Team (Frontend) | Interfaz de inicio de sesión y recuperación de contraseña (UI Angular) | Alta | 4h | Web |
| T016 | Development Team (Mobile) | Interfaz de autenticación de usuarios (UI Flutter) | Alta | 4h | Móvil |
| T017 | Development Team (Backend) | Implementación de gestión de productos y variantes (API REST) | Alta | 5h | Backend |
| T018 | Development Team (Frontend) | Interfaz de registro y edición de productos y variantes (UI Angular) | Alta | 5h | Web |
| T019 | Development Team (Backend) | Implementación de categorías y atributos de productos (API REST) | Media | 4h | Backend |
| T020 | Development Team (Frontend) | Interfaz de gestión de categorías y catálogo por empresa (UI Angular) | Alta | 4h | Web |
| T021 | Development Team (Backend) | Implementación de certificaciones y especificaciones técnicas (API REST) | Media | 4h | Backend |
| T022 | Development Team (Frontend) | Interfaz de gestión de certificaciones técnicas (UI Angular) | Media | 4h | Web |
| T023 | Development Team (Backend) | Implementación de gestión de actores de la cadena de suministro (API REST) | Media | 4h | Backend |
| T024 | Development Team (Backend) | Implementación de gestión de ubicaciones físicas (API REST) | Media | 4h | Backend |
| T025 | Development Team (Frontend) | Interfaz de actores y ubicaciones físicas (UI Angular) | Media | 4h | Web |

**Casos de uso cubiertos**

* **CU-004:** Autenticar y Recuperar Contraseña  
* **CU-006:** Gestionar Productos y Variantes  
* **CU-007:** Gestionar Certificaciones Técnicas  
* **CU-008:** Gestionar Catálogo por Empresa  
* **CU-009:** Gestionar Categorías de Productos  
* **CU-013:** Gestionar Actores de la Cadena  
* **CU-014:** Gestionar Ubicaciones Físicas

 **SPRINT 2 – Compras, unidades y logística**

**Objetivo**: desarrollar el seguimiento físico de las unidades de producto, las operaciones de compra y recepción, la generación de identificadores y códigos QR, además de los procesos logísticos.

| SPRINT 2 |  |  |  |  |  |
| ----- | :---- | :---- | :---- | :---- | :---- |
| **ID** | **ROL** | **Características / Funcionalidad** | **Prioridad** | **Tiempo estimado** | **Plataforma** |
| T026 | Development Team (Backend) | Implementación de gestión de órdenes de compra (API REST) | Alta | 5h | Backend |
| T027 | Development Team (Frontend) | Interfaz de creación y consulta de órdenes de compra (UI Angular) | Alta | 4h | Web |
| T028 | Development Team (Backend) | Implementación de aprobación y rechazo de órdenes de compra | Alta | 4h | Backend |
| T029 | Development Team (Backend) | Implementación de recepción de mercancía y actualización de existencias | Alta | 5h | Backend |
| T030 | Development Team (Frontend) | Interfaz de recepción y consulta de mercancía (UI Angular) | Alta | 4h | Web |
| T031 | Development Team (Backend) | Implementación de registro y gestión de unidades individuales | Alta | 5h | Backend |
| T032 | Development Team (Backend) | Asignación de identificadores únicos a unidades (Serial/IMEI/EID) | Alta | 4h | Backend |
| T033 | Development Team (Frontend) | Interfaz de administración de unidades individuales (UI Angular) | Alta | 4h | Web |
| T034 | Development Team (Backend) | Generación de códigos QR únicos por unidad | Alta | 4h | Backend |
| T035 | Development Team (Frontend) | Interfaz de generación y descarga de códigos QR (UI Angular) | Alta | 4h | Web |
| T036 | Development Team (Backend) | Implementación de envíos, movimientos y asignación de unidades | Alta | 5h | Backend |
| T037 | Development Team (Mobile) | Registro de recepción, transporte y condiciones mediante aplicación móvil | Alta | 5h | Móvil |

 

**Casos de uso cubiertos**

* **CU-010:** Gestionar Órdenes de Compra  
* **CU-011:** Aprobar / Rechazar Compra  
* **CU-012:** Gestionar Recepciones de Mercancía  
* **CU-015:** Gestionar Unidades de Producto  
* **CU-016:** Generar y Descargar Código QR  
* **CU-019:** Gestionar Envíos Logísticos  
* **CU-020:** Asignar / Desasignar Unidades a Envío  
* **CU-021:** Registrar Eventos y Condiciones de Transporte

 **SPRINT 3 – Trazabilidad, Blockchain y autenticidad**

**Objetivo**: implementar la trazabilidad digital de las unidades y su integración con Blockchain, permitiendo consultar el historial, verificar autenticidad, escanear códigos QR y registrar evidencias de las operaciones.

| SPRINT 3 |  |  |  |  |  |
| ----- | :---- | :---- | :---- | :---- | :---- |
| **ID** | **ROL** | **Características / Funcionalidad** | **Prioridad** | **Tiempo estimado** | **Plataforma** |
| T038 | Development Team (Backend) | Implementación del registro de eventos de trazabilidad (API REST) | Alta | 5h | Backend |
| T039 | Development Team (Blockchain) | Configuración de conexión con la red Blockchain Ethereum (Testnet) | Alta | 4h | Blockchain |
| T040 | Development Team (Blockchain) | Diseño del Smart Contract para registro de eventos | Alta | 5h | Blockchain |
| T041 | Development Team (Blockchain) | Implementación del registro de eventos mediante Smart Contract | Alta | 5h | Blockchain |
| T042 | Development Team (Backend) | Integración de FastAPI con Smart Contracts mediante Web3 | Alta | 5h | Backend |
| T043 | Development Team (Backend) | Asociación de eventos con actor, ubicación, fecha y transacción | Alta | 4h | Backend |
| T044 | Development Team (Backend) | Almacenamiento de hashes e identificadores Blockchain en PostgreSQL | Alta | 4h | Backend |
| T045 | Development Team (Blockchain) | Consulta y validación de registros Blockchain | Alta | 5h | Blockchain |
| T046 | Development Team (Mobile) | Escaneo de códigos QR mediante cámara del dispositivo (UI Flutter) | Alta | 4h | Móvil |
| T047 | Development Team (Mobile) | Consulta del historial y datos de trazabilidad mediante QR (UI Flutter) | Alta | 5h | Móvil |
| T048 | Development Team (Backend) | Verificación de autenticidad y reporte de falsificación (API REST) | Alta | 5h | Backend |
| T049 | Development Team (Backend) | Implementación de carga y asociación de documentos a unidades (API REST) | Media | 4h | Backend |

 

**Casos de uso cubiertos**

* **CU-017:** Escanear Código QR  
* **CU-018:** Registrar Consulta de Trazabilidad  
* **CU-022:** Consultar Historial y Verificar Autenticidad  
* **CU-023:** Reportar Sospecha de Falsificación  
* **CU-033:** Registrar Evento en Blockchain  
* **CU-034:** Consultar Registros Blockchain y Certificados  
* **CU-032:** Adjuntar Documentos a Unidades.

 **SPRINT 4 – Ventas, consumidor, devoluciones y reportes**

**Objetivo**: completar las funcionalidades comerciales y posteriores a la venta, permitiendo gestionar ventas, pagos, devoluciones, garantías, notificaciones, preferencias y reportes administrativos.

| SPRINT 4 |  |  |  |  |  |
| ----- | :---- | :---- | :---- | :---- | :---- |
| **ID** | **ROL** | **Características / Funcionalidad** | **Prioridad** | **Tiempo estimado** | **Plataforma** |
| T050 | Development Team (Backend) | Implementación de gestión de ventas y asignación de unidades (API REST) | Alta | 5h | Backend |
| T051 | Development Team (Frontend) | Interfaz de gestión de ventas y unidades asociadas (UI Angular) | Alta | 5h | Web |
| T052 | Development Team (Backend) | Implementación de pagos y registro de transacciones (API REST) | Media | 5h | Backend |
| T053 | Development Team (Backend) | Implementación de devoluciones y asignación de unidades devueltas | Alta | 5h | Backend |
| T054 | Development Team (Frontend) | Interfaz de devoluciones y garantías por unidad (UI Angular) | Alta | 4h | Web |
| T055 | Development Team (Backend) | Implementación de gestión de garantías por unidad (API REST) | Alta | 4h | Backend |
| T056 | Development Team (Backend) | Implementación de historial de compras y preferencias del usuario | Media | 4h | Backend |
| T057 | Development Team (Frontend) | Interfaz de historial de compras y preferencias (UI Angular) | Media | 4h | Web |
| T058 | Development Team (Backend) | Implementación de notificaciones y alertas de incidencias (API REST) | Alta | 5h | Backend |
| T059 | Development Team (Frontend) | Interfaz de notificaciones y alertas (UI Angular) | Media | 4h | Web |
| T060 | Development Team (Backend) | Generación de certificados digitales y reportes de trazabilidad | Alta | 5h | Backend |
| T061 | Development Team (Frontend) | Dashboard administrativo y visualización de reportes (UI Angular) | Alta | 5h | Web |

 

**Casos de uso cubiertos**

* **CU-005:** Consultar Bitácora y Gestionar Notificaciones  
* **CU-024:** Gestionar Alertas e Incidencias  
* **CU-025:** Gestionar Ventas  
* **CU-026:** Asignar Unidades Físicas a Venta  
* **CU-027:** Gestionar Pagos  
* **CU-028:** Consultar Historial de Compras del Consumidor  
* **CU-029:** Gestionar Devoluciones  
* **CU-030:** Asignar Unidades a Devolución  
* **CU-031:** Gestionar Garantías por Unidad  
* **CU-035:** Consultar Reportes y Dashboards

## **3.7. Requisitos Funcionales** 

| REQUISITOS FUNCIONALES |  |  |  |  |
| ----- | :---- | :---- | :---- | :---- |
| **ID** | **Funcionalidad** | **Descripción** | **Plataforma** | **Prioridad** |
| **RF-01** | **Autenticación de usuarios** | El sistema debe permitir el inicio y cierre de sesión mediante credenciales, generar y renovar tokens JWT, invalidar sesiones cerradas y limitar intentos repetidos de acceso. Las funcionalidades disponibles deben depender del rol del usuario. | Ambas | Alta |
| **RF-02** | **Gestión de roles y permisos** | El sistema debe permitir crear, editar y desactivar cuentas de usuario, asignar un rol principal y administrar los permisos asociados a cada rol dentro del alcance correspondiente (global o por empresa). Deben contemplarse los roles Super Administrador, Administrador de Empresa, Gestor de Operaciones, Gestor de Ventas y Postventa, Consumidor y Auditor. | Web / Backend | Alta |
| **RF-03** | **Registro y verificación de usuarios** | El sistema debe permitir el autorregistro de nuevas cuentas mediante formulario y verificación de correo electrónico, así como la creación y validación de cuentas operativas y de auditoría mediante aprobación administrativa. | Ambas | Alta |
| **RF-04** | **Recuperación de contraseña** | El sistema debe permitir solicitar la recuperación de contraseña mediante un enlace de verificación enviado por correo electrónico, y restablecerla de forma segura. | Ambas | Media |
| **RF-05** | **Bitácora de accesos y actividades** | El sistema debe registrar los intentos de inicio de sesión, cambios de contraseña y operaciones sensibles realizadas por los usuarios, permitiendo su consulta con fines de auditoría y supervisión. | Backend | Media |
| **RF-06** | **Gestión de empresas (tenants)** | El sistema debe permitir crear, configurar, suspender y eliminar empresas que operan sobre la plataforma, garantizando el aislamiento de los datos entre cada una. | Web / Backend | Alta |
| **RF-07** | **Registro de productos (catálogo)** | El sistema debe permitir registrar y editar productos del catálogo, incluyendo modelo, especificaciones técnicas, capacidad, color y precio base, manteniendo un historial de cambios. | Web | Alta |
| **RF-08** | **Gestión de categorías y atributos** | El sistema debe permitir crear, editar y organizar categorías y atributos diferenciadores de los productos del catálogo. | Web | Media |
| **RF-09** | **Registro de certificaciones técnicas** | El sistema debe permitir asociar certificaciones técnicas (FCC, CE, RoHS, Energy Star, garantía internacional del fabricante) a cada producto del catálogo y mostrarlas en su ficha. | Web | Media |
| **RF-10** | **Gestión de órdenes de compra e importación** | El sistema debe permitir registrar órdenes de compra a proveedores en el extranjero, someterlas a un flujo de aprobación y actualizar su estado durante el proceso de importación. | Web | Alta |
| **RF-11** | **Registro de unidades individuales** | El sistema debe permitir registrar cada unidad física recibida con su identificador único (número de serie, IMEI o EID) y vincularla a la orden de compra correspondiente. | Web | Alta |
| **RF-12** | **Generación de códigos QR/NFC** | El sistema debe generar automáticamente un código QR o etiqueta NFC único por unidad, derivado de su identificador, y permitir su impresión o descarga. | Backend | Alta |
| **RF-13** | **Registro de movimientos logísticos** | El sistema debe permitir registrar los movimientos de una unidad o envío, indicando origen, destino, fechas, medio de transporte y responsable de cada tramo. | Ambas | Alta |
| **RF-14** | **Registro de eventos de actores externos** | El sistema debe permitir asociar cada evento de trazabilidad a un participante externo de la cadena de suministro (proveedor, transportista, autoridad aduanera), sin requerir que dicho participante cuente con una cuenta en el sistema. | Backend | Alta |
| **RF-15** | **Registro de condiciones de transporte** | El sistema debe permitir registrar condiciones de transporte (temperatura, humedad, vibración) de cada envío, de forma manual o mediante integración con sensores IoT. | Móvil / Backend | Alta |
| **RF-16** | **Registro de incidencias en la cadena de suministro** | El sistema debe permitir registrar incidencias ocurridas durante el transporte, el despacho aduanero o el almacenamiento, clasificándolas por tipo y gravedad. | Ambas | Alta |
| **RF-17** | **Gestión de devoluciones y garantías** | El sistema debe permitir registrar devoluciones asociadas a una unidad, gestionar el estado de su garantía y adjuntar documentos de respaldo. | Web | Alta |
| **RF-18** | **Historial de trazabilidad** | El sistema debe construir y presentar el historial cronológico completo de una unidad, desde su compra en el país de origen hasta su entrega al consumidor final. | Ambas | Alta |
| **RF-19** | **Registro de eventos en blockchain** | El sistema debe registrar de forma inmutable en la red blockchain los eventos críticos de trazabilidad, generando un hash y una marca de tiempo verificable para cada uno. | Backend / Blockchain | Alta |
| **RF-20** | **Consulta de registros blockchain** | El sistema debe permitir consultar los registros almacenados en blockchain y comparar su integridad frente a los datos operativos almacenados en la base de datos relacional. | Web / Backend | Alta |
| **RF-21** | **Verificación de autenticidad del producto** | El sistema debe permitir verificar la autenticidad y el origen legal de un dispositivo a partir de su identificador digital y sus registros de trazabilidad. | Ambas | Alta |
| **RF-22** | **Escaneo de código QR/NFC** | El sistema debe permitir escanear el código de una unidad mediante la cámara o el lector NFC del dispositivo y consultar de inmediato la información asociada. | Móvil | Alta |
| **RF-23** | **Acceso público sin registro** | El sistema debe permitir consultar el historial de trazabilidad de una unidad escaneada sin necesidad de registro ni inicio de sesión. | Ambas | Media |
| **RF-24** | **Portal de consulta del consumidor y exposición externa**  | El sistema debe presentar el origen, las condiciones de transporte, el despacho aduanero y el estado de autenticidad de la unidad consultada, en un formato claro y comprensible. Esta misma información debe estar disponible mediante una API REST documentada (OpenAPI/Swagger) y autenticada con clave de API, permitiendo que plataformas e-commerce externas consulten y visualicen el historial de trazabilidad dentro de su propia ficha de producto, sin que el sistema gestione el proceso de compra. | Ambas | Alta |
| **RF-25** | **Favoritos e historial personal** | El sistema debe permitir guardar unidades como favoritas y consultar el historial de escaneos y compras previas asociado a la cuenta del usuario. | Ambas | Media |
| **RF-26** | **Reporte de sospecha de falsificación** | El sistema debe permitir reportar una unidad sospechosa de falsificación o irregularidad, registrando la denuncia junto con la evidencia proporcionada. | Ambas | Media |
| **RF-27** | **Generación de certificados digitales** | El sistema debe generar automáticamente un certificado digital de trazabilidad para cada unidad al momento de su venta, respaldado por los registros almacenados en blockchain. | Backend / Web | Alta |
| **RF-28** | **Descarga y visualización de certificados** | El sistema debe permitir visualizar y descargar en formato PDF el certificado digital de trazabilidad de una unidad. | Ambas | Alta |
| **RF-29** | **Notificaciones y alertas** | El sistema debe generar y enviar notificaciones ante incidencias, retiros de producto o eventos relevantes asociados a las unidades del usuario. | Ambas | Alta |
| **RF-30** | **Reportes y análisis de trazabilidad** | El sistema debe presentar indicadores y reportes sobre tiempos de importación, incidencias, ventas, cumplimiento normativo y estado de la cadena de suministro, permitiendo aplicar filtros por periodo y exportar la información cuando corresponda. | Web | Alta |

 

## **3.8. Requisitos no funcionales**

| REQUISITOS NO FUNCIONALES |  |  |  |  |  |  |  |  |  |  |
| ----- | :---- | ----- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **ID** | **Requisito no funcional** | **Vers.** | **Actores** | **Objetivo asociado** | **Requisitos asociados** | **Descripción** | **Importancia** | **Urgencia** | **Estabilidad** | **Comentarios** |
| RNF-01 | Rendimiento: Tiempo de respuesta en consultas críticas | 1 | Todos | Garantizar tiempos de respuesta rápidos en consultas y gestiones críticas | RF-18, RF-21, RF-22, RF-24 | El sistema debe garantizar un tiempo de respuesta promedio ≤2 segundos para operaciones críticas de consulta y gestión (excluye confirmación blockchain, ver RNF-19). | Alta | Alta | Alta | Medible con pruebas de carga. |
| RNF-02 | Disponibilidad: Continuidad operativa del sistema | 1 | Todos | Mantener el sistema operativo la mayor parte del tiempo | RF-13, RF-18, RF-19, RF-29 | El sistema debe mantener una disponibilidad mínima del 99,5% durante su operación, considerando la infraestructura desplegada en la nube. | Alta | Media | Alta | Depende del proveedor cloud. |
| RNF-03 | Escalabilidad: Crecimiento de empresas y volumen de datos | 1 | Super Administrador, Administrador de Empresa | Permitir el crecimiento de empresas, usuarios y eventos sin rediseñar la arquitectura | RF-06, RF-07, RF-10, RF-13, RF-19, RF-30 | La arquitectura debe permitir incrementar recursos de servidores y nodos para soportar el crecimiento de empresas, usuarios, productos y eventos de trazabilidad. | Alta | Media | Media | Prioritario por el modelo multi-tenant. |
| RNF-04 | Seguridad: Autenticación y comunicaciones seguras | 1 | Todos | Proteger credenciales y comunicaciones del sistema | RF-01, RF-02, RF-03, RF-04 | El sistema debe proteger credenciales y comunicaciones mediante autenticación, autorización y cifrado de datos en tránsito (HTTPS/TLS). | Vital | Inmediata | Alta | Base de la confianza del sistema. |
| RNF-05 | Control de acceso: Permisos según rol | 1 | Todos | Restringir funciones y datos según el rol del usuario | RF-01, RF-02 | El sistema debe garantizar que cada usuario acceda únicamente a las funcionalidades y datos correspondientes a su rol. | Vital | Inmediata | Alta | Complementa a RNF-13 (aislamiento entre empresas). |
| RNF-06 | Integridad de datos: Consistencia de la información operativa | 1 | Gestor de Operaciones, Administrador de Empresa | Mantener consistencia de la información operativa almacenada | RF-07, RF-10, RF-11, RF-13, RF-16 | La información almacenada en la base de datos debe conservar consistencia mediante validaciones y transacciones controladas. | Alta | Alta | Alta | Aplica a PostgreSQL. |
| RNF-07 | Inmutabilidad: Registros blockchain no alterables | 1 | Gestor de Operaciones, Auditor, Super Administrador | Garantizar que los eventos registrados no puedan alterarse retroactivamente | RF-19, RF-20 | Los eventos registrados en blockchain deben conservarse de forma inmutable, permitiendo detectar cualquier alteración. | Vital | Inmediata | Alta | Pilar tecnológico central del proyecto. |
| RNF-08 | Auditabilidad: Trazabilidad de actores y eventos | 1 | Auditor, Super Administrador | Permitir reconstruir el historial de responsables y eventos del sistema | RF-05, RF-18, RF-20, RF-30 | Los eventos de trazabilidad deben permitir identificar al actor responsable, fecha, hora e información asociada a cada operación registrada. | Alta | Media | Alta | Respaldado directamente por el rol Auditor. |
| RNF-09 | Interoperabilidad: Integración con sistemas externos | 1 | Administrador de Empresa, Gestor de Ventas y Postventa | Permitir integración con plataformas externas de comercio electrónico y ERP | RF-24, RF-27 | El sistema debe exponer APIs REST documentadas para la comunicación entre backend, plataforma web, app móvil y servicios externos. | Media | Media | Media | Depende de acuerdos con terceros. |
| RNF-10 | Usabilidad: Facilidad de uso por rol | 1 | Consumidor Registrado, Gestor de Operaciones, Gestor de Ventas y Postventa | Facilitar el uso del sistema sin conocimientos técnicos especializados | RF-13, RF-22, RF-24 | Las interfaces web y móvil deben permitir a un usuario nuevo completar las tareas principales de su rol en un máximo de 3 intentos durante pruebas de usabilidad. | Media | Media | Media | Métrica verificable en pruebas. |
| RNF-11 | Compatibilidad: Soporte multiplataforma | 1 | Consumidor Registrado, Gestor de Operaciones | Garantizar el funcionamiento en distintos dispositivos y navegadores | RF-22, RF-23 | La app móvil debe funcionar en dispositivos Android e iOS compatibles con Flutter; la plataforma web debe ser accesible desde navegadores modernos. | Alta | Media | Media | — |
| RNF-12 | Mantenibilidad: Arquitectura modular | 1 | Super Administrador (equipo técnico) | Facilitar la actualización de componentes sin afectar el sistema completo | RF-01 a RF-30 | El sistema debe utilizar una arquitectura modular que facilite el mantenimiento y actualización independiente de sus componentes. | Media | Media | Media | Aplica transversalmente a toda la plataforma. |
| RNF-13 | Aislamiento multi-tenant: Separación de datos entre empresas | 1 | Super Administrador, Administrador de Empresa | Evitar que los datos de una empresa sean visibles para otra | RF-06, RF-07 | El sistema debe garantizar que los datos de una empresa (tenant) nunca sean accesibles ni visibles para usuarios de otra empresa, independientemente del rol que compartan. | Vital | Inmediata | Alta | Crítico para el modelo multiempresa. |
| RNF-14 | Privacidad: Protección de datos personales y comerciales | 1 | Consumidor Registrado, Gestor de Ventas y Postventa, Auditor | Proteger la confidencialidad de datos personales y documentación comercial sensible | RF-10, RF-17, RF-25 | El sistema debe proteger la confidencialidad de los datos personales de consumidores y de la documentación comercial sensible (facturas, documentos aduaneros), restringiendo su acceso según rol y propósito. | Vital | Alta | Alta | Relacionado con documentación aduanera y garantías. |
| RNF-15 | Seguridad: Gestión de claves criptográficas | 1 | Super Administrador | Evitar la exposición de claves privadas usadas en blockchain | RF-19, RF-20 | El sistema debe almacenar y gestionar las claves privadas para firmar transacciones en blockchain mediante un servicio dedicado de gestión de secretos, evitando su exposición en código o configuración. | Vital | Inmediata | Alta | Soporta la garantía de inmutabilidad (RNF-07). |
| RNF-16 | Continuidad: Recuperación ante desastres | 1 | Super Administrador | Restaurar el sistema ante fallos de infraestructura | RF-06, RF-18 | El sistema debe contar con copias de respaldo periódicas de la base de datos y procedimientos de recuperación con un tiempo objetivo de restauración definido. | Alta | Media | Media | Depende del proveedor cloud. |
| RNF-17 | Consistencia: Sincronización base de datos–blockchain | 1 | Gestor de Operaciones, Super Administrador | Sincronizar los registros operativos con los registros en blockchain | RF-19, RF-20 | El sistema debe garantizar que todo evento registrado en la base de datos relacional finalice sincronizado con su correspondiente registro en blockchain, aunque no sea en tiempo real. | Alta | Alta | Media | Riesgo propio de la arquitectura híbrida. |
| RNF-18 | Disponibilidad: Modo offline de la app móvil | 1 | Consumidor Registrado, Gestor de Operaciones | Permitir la consulta de productos escaneados sin conexión a internet | RF-22, RF-25 | La aplicación móvil debe permitir consultar productos previamente escaneados sin conexión, sincronizando la información al restablecerse la conectividad. | Media | Media | Media | Aplica solo a la app móvil (Flutter). |
| RNF-19 | Rendimiento: Latencia de confirmación blockchain | 1 | Gestor de Operaciones, Consumidor Registrado | Informar al usuario que un evento fue enviado a blockchain sin esperar la confirmación final de red | RF-19 | El sistema debe confirmar visualmente al usuario, en un máximo de 2 segundos, que un evento fue enviado a blockchain, mostrando su estado como "pendiente" hasta que la red confirme la transacción. | Alta | Alta | Media | Evita la percepción de lentitud del sistema. |

## 

## **3.9. Lista de casos de uso (web y móvil)**

| ID | Caso de uso | Sprint | Web | Móvil | Prioridad |
| ----- | ----- | ----- | ----- | ----- | ----- |
| CU-001 | Gestionar Empresas (Tenants) | 0 | ✓ | — | Alta |
| CU-002 | Gestionar Usuarios del Sistema | 0 | ✓ | — | Alta |
| CU-003 | Asignar Roles y Permisos a Usuario | 0 | ✓ | — | Alta |
| CU-004 | Autenticar y Recuperar Contraseña | 1 | ✓ | ✓ | Alta |
| CU-005 | Consultar Bitácora y Gestionar Notificaciones | 3 | ✓ | ✓ | Media |
| CU-006 | Gestionar Productos y Variantes | 1 | ✓ | — | Alta |
| CU-007 | Gestionar Certificaciones Técnicas | 1 | ✓ | — | Media |
| CU-008 | Gestionar Catálogo por Empresa | 1 | ✓ | — | Alta |
| CU-009 | Gestionar Categorías de Productos | 1 | ✓ | — | Media |
| CU-010 | Gestionar Órdenes de Compra | 2 | ✓ | — | Alta |
| CU-011 | Aprobar / Rechazar Compra | 2 | ✓ | — | Alta |
| CU-012 | Gestionar Recepciones de Mercancía | 2 | ✓ | — | Alta |
| CU-013 | Gestionar Actores de la Cadena | 1 | ✓ | — | Media |
| CU-014 | Gestionar Ubicaciones Físicas | 1 | ✓ | — | Media |
| CU-015 | Gestionar Unidades de Producto (Serial/IMEI) | 1 | ✓ | — | Alta |
| CU-016 | Generar y Descargar Código QR | 2 | ✓ | — | Alta |
| CU-017 | Escanear Código QR | 3 | — | ✓ | Alta |
| CU-018 | Registrar Consulta de Trazabilidad | 3 | ✓ (Backend) | ✓ (Backend) | Alta |
| CU-019 | Gestionar Envíos Logísticos | 2 | ✓ | — | Alta |
| CU-020 | Asignar / Desasignar Unidades a Envío | 2 | ✓ | — | Alta |
| CU-021 | Registrar Eventos y Condiciones de Transporte | 2 | ✓ | ✓ | Alta |
| CU-022 | Consultar Historial y Verificar Autenticidad | 3 | ✓ | ✓ | Alta |
| CU-023 | Reportar Sospecha de Falsificación | 3 | — | ✓ | Media |
| CU-024 | Gestionar Alertas e Incidencias | 3 | ✓ | ✓ | Alta |
| CU-025 | Gestionar Ventas | 4 | ✓ | — | Alta |
| CU-026 | Asignar Unidades Físicas a Venta | 4 | ✓ | — | Alta |
| CU-027 | Gestionar Pagos | 4 | ✓ | — | Media |
| CU-028 | Consultar Historial de Compras del Consumidor | 4 | ✓ | ✓ | Media |
| CU-029 | Gestionar Devoluciones | 4 | ✓ | — | Alta |
| CU-030 | Asignar Unidades a Devolución | 4 | ✓ | — | Alta |
| CU-031 | Gestionar Garantías por Unidad | 4 | ✓ | — | Alta |
| CU-032 | Adjuntar Documentos a Unidades | 2 | ✓ | — | Media |
| CU-033 | Registrar Evento en Blockchain | 3 | ✓ (Backend) | — | Alta |
| CU-034 | Consultar Registros Blockchain y Certificados | 3 | ✓ | ✓ (lectura) | Alta |
| CU-035 | Gestionar Reportes y Dashboards | 4 | ✓ | — | Alta |

## **3.10. Paquetes y casos de Uso**

**3.10.1 P1. Seguridad y Multi-Tenant**    
**3.10.2. P2. Catálogo y Abastecimiento**    
**3.10.3. P3. Actores y Ubicaciones**    
**3.10.4. P4. Inventario y Trazabilidad (Núcleo)**    
**3.10.5. P5. Comercialización (Ventas y Postventa)**    
**3.10.6. P6. Blockchain y Certificados**    
**3.10.7. P7. Reportes y Administración** 

| Paquete | Módulo(s) asociado(s) | Casos de uso incluidos | Cantidad | Actores principales |
| ----- | ----- | ----- | ----- | ----- |
| **P1. Seguridad y Multi-Tenant** | 5.1.1 | CU-001, CU-002, CU-003, CU-004, CU-005 | 5 | Super Administrador, Administrador de Empresa, todos los usuarios con cuenta |
| **P2. Catálogo y Abastecimiento** | 5.1.2, 5.1.3 | CU-006, CU-007, CU-008, CU-009, CU-010, CU-011, CU-012 | 7 | Administrador de Empresa, Gestor de Operaciones |
| **P3. Actores y Ubicaciones** | 5.1.4 | CU-013, CU-014 | 2 | Administrador de Empresa |
| **P4. Inventario y Trazabilidad (Núcleo)** | 5.1.5 | CU-015, CU-016, CU-017, CU-018, CU-019, CU-020, CU-021, CU-022, CU-023, CU-024 | 10 | Gestor de Operaciones, Consumidor Registrado, Visitante Anónimo, Auditor |
| **P5. Comercialización (Ventas y Postventa)** | 5.1.6, 5.1.7 | CU-025, CU-026, CU-027, CU-028, CU-029, CU-030, CU-031, CU-032 | 8 | Gestor de Ventas y Postventa, Consumidor Registrado, Super Administrador (en CU-027) |
| **P6. Blockchain y Certificados** | 5.1.8 | CU-033, CU-034 | 2 | Sistema (Smart Contract), Auditor, Super Administrador, Consumidor Registrado |
| **P7. Reportes y Administración** | Transversal | CU-035 | 1 | Administrador de Empresa, Super Administrador |

