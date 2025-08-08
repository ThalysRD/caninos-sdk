#!/usr/bin/env python3
"""
Teste de compatibilidade e mapeamento correto para 32-bits
"""

import caninos_sdk as k9
import logging

# Habilitar logs para debug
logging.basicConfig(level=logging.INFO)

def test_board_detection():
    """Testa a detecção automática da placa"""
    print("🔍 TESTE DE DETECÇÃO DA PLACA")
    print("=" * 35)
    
    try:
        labrador = k9.Labrador()
        
        print(f"✅ CPU Architecture: {labrador.cpu_architecture}")
        print(f"✅ Board Version: {labrador.board_version}-bit")
        print(f"✅ Kernel Version: {labrador.kernel_version}")
        
        if labrador.cpu_architecture == "armv7l":
            if labrador.board_version == "32":
                print("✅ CORRETO: armv7l → 32-bit detectado")
                return True
            else:
                print(f"❌ ERRO: armv7l deveria ser 32-bit, mas detectou {labrador.board_version}-bit")
                return False
        elif labrador.cpu_architecture == "aarch64":
            if labrador.board_version == "64":
                print("✅ CORRETO: aarch64 → 64-bit detectado")
                return True
            else:
                print(f"❌ ERRO: aarch64 deveria ser 64-bit, mas detectou {labrador.board_version}-bit")
                return False
        else:
            print(f"⚠️  Arquitetura não reconhecida: {labrador.cpu_architecture}")
            return True  # Pode ser desenvolvimento
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

def test_pin_mappings():
    """Testa os mapeamentos de pinos baseados na tabela oficial"""
    print("\n🔍 TESTE DOS MAPEAMENTOS")
    print("=" * 30)
    
    try:
        labrador = k9.Labrador()
        board_version = labrador.board_version
        
        print(f"Testando mapeamentos para placa {board_version}-bit:")
        
        # Pinos importantes para testar baseados na tabela oficial
        test_pins = {
            3: "E2",    # I2C0_SDA
            5: "E3",    # I2C0_SCL
            7: "B18",   # PCM_SYNC
            11: "C0",   # PCM_CLK
            13: "C1",   # PCM_DIN
            15: "C4",   # DSI_CP/SD1_D1/LCDD_D1 (GPIO que você testou)
            18: "C6",   # DSI_DN/SD1_D3/LCDD_D3
            22: "C5",   # DSI_CN/SD1_D2/LCDD_D2
            33: "B0",   # PWM0
            35: "B1",   # PWM2
            37: "B2",   # PWM4
        }
        
        success_count = 0
        total_count = 0
        
        for pin, expected_group in test_pins.items():
            chip_id, line_id = k9.Pin.get_num(pin, board_version)
            total_count += 1
            
            if chip_id is not None and line_id is not None:
                actual_group = chr(ord('A') + chip_id) + str(line_id)
                
                if actual_group == expected_group:
                    print(f"✅ Pin {pin:2d}: {expected_group} → chip{chip_id}, line{line_id}")
                    success_count += 1
                else:
                    print(f"❌ Pin {pin:2d}: esperado {expected_group}, obteve {actual_group}")
            else:
                print(f"❌ Pin {pin:2d}: mapeamento falhou")
        
        print(f"\n📊 Resultado: {success_count}/{total_count} mapeamentos corretos")
        return success_count == total_count
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gpio15_specifically():
    """Teste específico do GPIO 15 (o que você testou manualmente)"""
    print("\n🎯 TESTE ESPECÍFICO GPIO 15")
    print("=" * 30)
    
    try:
        labrador = k9.Labrador()
        
        # Verificar mapeamento
        chip_id, line_id = k9.Pin.get_num(15, labrador.board_version)
        
        print(f"GPIO 15 mapeia para: chip{chip_id}, line{line_id}")
        
        # Para 32-bit, baseado na tabela oficial: HEADER 15 → GPIOC4 → GPIO 68
        # Para chardev: C=2, linha 4
        if labrador.board_version == "32":
            if chip_id == 2 and line_id == 4:
                print("✅ Mapeamento GPIO 15 está CORRETO para 32-bit!")
                print("   GPIO 15 → gpiochip2, line4 (GPIOC4)")
                
                # Criar pin object para teste
                try:
                    pin15 = k9.Pin(15, labrador)
                    print(f"✅ Pin object criado: {pin15}")
                    print(f"   chip_id={pin15.chip_id}, line_id={pin15.line_id}")
                    return True
                except Exception as e:
                    print(f"❌ Erro criando Pin object: {e}")
                    return False
            else:
                print(f"❌ Mapeamento GPIO 15 INCORRETO!")
                print(f"   Esperado: chip2, line4")
                print(f"   Obtido: chip{chip_id}, line{line_id}")
                return False
        else:
            print(f"⚠️  Testando em placa {labrador.board_version}-bit (não é 32-bit)")
            return True
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_available_pins():
    """Mostra todos os pinos disponíveis"""
    print("\n📋 PINOS DISPONÍVEIS")
    print("=" * 25)
    
    try:
        labrador = k9.Labrador()
        board_version = labrador.board_version
        
        from caninos_sdk.pin import gpio_mappings
        
        if board_version in gpio_mappings:
            mappings = gpio_mappings[board_version]
            
            print(f"Pinos disponíveis para {board_version}-bit:")
            print("Pin | Grupo | Chip | Line | Função")
            print("----|-------|------|------|--------")
            
            for pin in sorted(mappings.keys()):
                group = mappings[pin]
                chip_id = ord(group[0]) - ord('A')
                line_id = int(group[1:])
                
                # Adicionar informação de função baseada na tabela
                functions = {
                    3: "I2C0_SDA",
                    5: "I2C0_SCL", 
                    7: "PCM_SYNC",
                    8: "UART0_TX",
                    10: "UART0_RX",
                    11: "PCM_CLK",
                    12: "I2S_BCLK",
                    13: "PCM_DIN",
                    15: "SD1_D1/LCDD_D1",
                    18: "SD1_D3/LCDD_D3",
                    19: "SPI2_MOSI",
                    21: "SPI2_MISO",
                    22: "SD1_D2/LCDD_D2",
                    23: "SPI2_SCLK",
                    24: "SPI2_SS",
                    26: "PCM_DOUT",
                    33: "PWM0",
                    35: "PWM2",
                    37: "PWM4",
                }
                
                func = functions.get(pin, "GPIO")
                print(f"{pin:3d} |  {group}   |  {chip_id}   |  {line_id:2d}  | {func}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 TESTE DE COMPATIBILIDADE CANINOS SDK 32-BIT")
    print("=" * 50)
    
    # 1. Teste de detecção da placa
    detection_ok = test_board_detection()
    
    # 2. Teste dos mapeamentos
    mappings_ok = test_pin_mappings()
    
    # 3. Teste específico do GPIO 15
    gpio15_ok = test_gpio15_specifically()
    
    # 4. Mostrar pinos disponíveis
    show_available_pins()
    
    # Resultado final
    print(f"\n✨ RESUMO DOS TESTES")
    print("=" * 25)
    print(f"Detecção da placa: {'✅ OK' if detection_ok else '❌ FALHOU'}")
    print(f"Mapeamentos: {'✅ OK' if mappings_ok else '❌ FALHOU'}")
    print(f"GPIO 15: {'✅ OK' if gpio15_ok else '❌ FALHOU'}")
    
    if detection_ok and mappings_ok and gpio15_ok:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("A SDK está corretamente configurada para 32-bit!")
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM")
        print("Verifique os erros acima para correções necessárias.")

if __name__ == "__main__":
    main()
