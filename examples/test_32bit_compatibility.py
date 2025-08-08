#!/usr/bin/env python3
"""
Teste de compatibilidade para placa Caninos Labrador 32-bit
Quad-core ARM Cortex-A9R4 CPU, 2GB LPDDR3, 16GB eMMC

Este script testa as funcionalidades básicas da SDK na placa de 32 bits.
"""

import caninos_sdk as k9
import time
import logging

def test_board_detection():
    """Testa a detecção automática da placa"""
    print("=== Teste de Detecção da Placa ===")
    labrador = k9.Labrador()
    
    print(f"Arquitetura CPU: {labrador.cpu_architecture}")
    print(f"Versão da placa: {labrador.board_version}-bit")
    print(f"Versão do kernel: {labrador.kernel_version}")
    print(f"Recursos habilitados: {len(labrador.enabled_features)}")
    
    # Verificar se é uma placa ARM de 32 bits
    if labrador.cpu_architecture == "armv7l" and labrador.board_version == "32":
        print("✅ Placa ARM Cortex-A9R4 32-bit detectada corretamente!")
    else:
        print(f"ℹ️  Executando em: {labrador.cpu_architecture} ({labrador.board_version}-bit)")
    
    return labrador

def test_gpio_basic(labrador):
    """Testa GPIO básico"""
    print("\n=== Teste GPIO Básico ===")
    
    try:
        # Testar pino 15 (muito comum nos exemplos)
        labrador.pin15.enable_gpio(k9.Pin.Direction.OUTPUT, alias="led_test")
        print("✅ Pino 15 habilitado como saída")
        
        # Testar alguns ciclos de on/off
        for i in range(3):
            print(f"  Ciclo {i+1}: LED ligado")
            labrador.led_test.high()
            time.sleep(0.5)
            
            print(f"  Ciclo {i+1}: LED desligado")
            labrador.led_test.low()
            time.sleep(0.5)
            
        print("✅ Teste de GPIO básico concluído")
        
    except Exception as e:
        print(f"❌ Erro no teste GPIO: {e}")
        return False
    
    return True

def test_pin_mapping_32bit():
    """Testa o mapeamento específico de pinos para 32-bit"""
    print("\n=== Teste Mapeamento de Pinos 32-bit ===")
    
    # Pinos específicos da versão 32-bit
    test_pins = [15, 19, 22, 18]  # Inclui pino 19 que tem "C25" só na versão 32-bit
    
    for pin in test_pins:
        try:
            chip_id, line_id = k9.Pin.get_num(pin, "32")
            if chip_id is not None and line_id is not None:
                print(f"✅ Pino {pin}: chip{chip_id}, linha{line_id}")
            else:
                print(f"❌ Pino {pin}: mapeamento falhou")
        except Exception as e:
            print(f"❌ Pino {pin}: erro - {e}")

def test_i2c_availability(labrador):
    """Testa disponibilidade do I2C"""
    print("\n=== Teste I2C ===")
    
    try:
        available_ports = labrador.i2c.list_ports()
        print(f"Portas I2C disponíveis: {available_ports}")
        
        if "/dev/i2c-2" in available_ports:
            print("✅ Porta I2C padrão (/dev/i2c-2) encontrada")
        else:
            print("⚠️  Porta I2C padrão não encontrada")
            
    except Exception as e:
        print(f"❌ Erro ao testar I2C: {e}")

def test_serial_availability(labrador):
    """Testa disponibilidade das portas seriais"""
    print("\n=== Teste Serial ===")
    
    try:
        available_ports = labrador.serial_usb.list_ports()
        print(f"Portas seriais disponíveis: {available_ports}")
        
        if k9.SERIAL_USB in available_ports:
            print(f"✅ Porta USB serial ({k9.SERIAL_USB}) encontrada")
        if k9.SERIAL_HEADER_40_PINS in available_ports:
            print(f"✅ Porta serial do header 40 pinos ({k9.SERIAL_HEADER_40_PINS}) encontrada")
            
    except Exception as e:
        print(f"❌ Erro ao testar Serial: {e}")

def main():
    """Função principal de teste"""
    print("Caninos SDK - Teste de Compatibilidade 32-bit")
    print("=" * 50)
    
    # Configurar logging para ver mais detalhes
    logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Detectar placa
        labrador = test_board_detection()
        
        # Testar mapeamento de pinos
        test_pin_mapping_32bit()
        
        # Testar periféricos
        test_i2c_availability(labrador)
        test_serial_availability(labrador)
        
        # Testar GPIO (só se não estiver em PC)
        if labrador.cpu_architecture != "x86_64":
            success = test_gpio_basic(labrador)
            if success:
                print("\n🎉 Todos os testes de GPIO passaram!")
            else:
                print("\n⚠️  Alguns testes de GPIO falharam")
        else:
            print("\n🖥️  Executando em PC - testes de GPIO pulados")
            
        print("\n✅ Teste de compatibilidade concluído")
        
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
