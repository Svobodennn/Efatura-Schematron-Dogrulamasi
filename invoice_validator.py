#!/usr/bin/env python3
import sys
import os
from lxml import etree

class InvoiceValidator:
    def __init__(self, schematron_path):
        """Schematron dosyası ile doğrulayıcıyı başlatır."""
        self.schematron_path = schematron_path
        self.schematron = None
        self.base_dir = os.path.dirname(os.path.abspath(schematron_path))
        # Schematron için gerekli namespace'leri ayarla
        self.nsmap = {
            'sch': 'http://purl.oclc.org/dsdl/schematron',
            'sh': 'http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader',
            'ef': 'http://www.efatura.gov.tr/package-namespace',
            'inv': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
            'apr': 'urn:oasis:names:specification:ubl:schema:xsd:ApplicationResponse-2',
            'desp': 'urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2',
            'recp': 'urn:oasis:names:specification:ubl:schema:xsd:ReceiptAdvice-2',
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
            'ds': 'http://www.w3.org/2000/09/xmldsig#',
            'xades': 'http://uri.etsi.org/01903/v1.3.2#',
            'hr': 'http://www.hr-xml.org/3',
            'oa': 'http://www.openapplications.org/oagis/9',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'ubl': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
            'ccts': 'urn:un:unece:uncefact:documentation:2',
            'ubltr': 'urn:oasis:names:specification:ubl:schema:xsd:TurkishCustomizationExtensionComponents',
            'qdt': 'urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2',
            'udt': 'urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2'
        }
        self._load_schematron()

    def _process_includes(self, schema_doc):
        """Dahil edilen Schematron dosyalarını işler."""
        # sch: namespace'i ile dahil edilen tüm elementleri bul
        includes = schema_doc.xpath('//sch:include', namespaces=self.nsmap)
        
        for include in includes:
            href = include.get('href')
            if href:
                # href'i dosya ve fragment olarak ayır
                file_part, fragment = href.split('#') if '#' in href else (href, None)
                
                # Tam dosya yolunu oluştur
                include_path = os.path.join(self.base_dir, file_part)
                
                try:
                    # Dahil edilen dosyayı ayrıştır
                    with open(include_path, 'rb') as f:
                        included_doc = etree.parse(f)
                    
                    # Eğer fragment varsa, o belirli elementi al
                    if fragment:
                        included_elements = included_doc.xpath(f'//*[@id="{fragment}"]', namespaces=self.nsmap)
                        if included_elements:
                            # Dahil edilen içeriği include elementi ile değiştir
                            parent = include.getparent()
                            index = parent.index(include)
                            for element in included_elements:
                                parent.insert(index, element)
                            parent.remove(include)
                except Exception as e:
                    print(f"Uyarı: {href} dahil edilemedi: {e}")
                    # Doğrulamaya devam etmek için include elementini kaldır
                    parent = include.getparent()
                    if parent is not None:
                        parent.remove(include)

    def _load_schematron(self):
        """Schematron dosyasını yükler ve derler."""
        try:
            # Tüm namespace'leri kaydet
            for prefix, uri in self.nsmap.items():
                etree.register_namespace(prefix, uri)
                
            # Schematron dosyasını XML ağacına ayrıştır
            parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
            with open(self.schematron_path, 'rb') as f:
                self.schematron = etree.parse(f, parser=parser)
                
            # Dahil edilen dosyaları işle
            self._process_includes(self.schematron)
            
        except Exception as e:
            print(f"Schematron dosyası yüklenirken hata: {e}")
            sys.exit(1)

    def validate(self, xml_path):
        """XML dosyasını Schematron kurallarına göre doğrular."""
        try:
            # XML dosyasını namespace desteği ile ayrıştır
            parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
            with open(xml_path, 'rb') as f:
                xml_doc = etree.parse(f, parser=parser)
            
            # Schematron'dan tüm kuralları al
            rules = self.schematron.xpath('//sch:rule', namespaces=self.nsmap)
            
            errors = []
            for rule in rules:
                context = rule.get('context')
                if context:
                    try:
                        # Bu kuralın bağlamına uyan tüm düğümleri bul
                        context_nodes = xml_doc.xpath(context, namespaces=self.nsmap)
                        
                        # Bu kural için tüm iddiaları al
                        assertions = rule.xpath('.//sch:assert', namespaces=self.nsmap)
                        
                        for node in context_nodes:
                            for assertion in assertions:
                                test = assertion.get('test')
                                message = assertion.text
                                
                                # Mevcut düğüm için bağlam sözlüğü oluştur
                                variables = {}
                                for let in self.schematron.xpath('//sch:let', namespaces=self.nsmap):
                                    name = let.get('name')
                                    value = let.get('value')
                                    if name and value:
                                        try:
                                            variables[name] = xml_doc.xpath(value, namespaces=self.nsmap)
                                        except:
                                            pass
                                
                                # Test ifadesini bağlamda değerlendir
                                try:
                                    result = xml_doc.xpath(test, namespaces=self.nsmap, smart_strings=False, variables=variables)
                                    if not result:
                                        errors.append(f"Başarısız iddia: {message}")
                                except Exception as e:
                                    errors.append(f"İddia değerlendirilirken hata: {test} - {str(e)}")
                    except Exception as e:
                        errors.append(f"Kural bağlamı işlenirken hata {context}: {str(e)}")
            
            if not errors:
                print("✅ Fatura geçerli!")
                return True
            else:
                print("❌ Fatura doğrulaması başarısız!")
                for error in errors:
                    print(f"  - {error}")
                return False
                
        except Exception as e:
            print(f"XML dosyası doğrulanırken hata: {e}")
            return False

def main():
    if len(sys.argv) != 3:
        print("Kullanım: python invoice_validator.py <schematron_dosyası> <xml_dosyası>")
        sys.exit(1)

    schematron_path = sys.argv[1]
    xml_path = sys.argv[2]

    validator = InvoiceValidator(schematron_path)
    validator.validate(xml_path)

if __name__ == "__main__":
    main() 