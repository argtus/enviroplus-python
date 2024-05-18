import pytest


def test_gas_setup(gpiod, gpiodevice, smbus, GPIO, gas):
    from enviroplus import gas
    gas._is_setup = False
    gas.setup()


def test_gas_unavailable(gpiod, gpiodevice, mocksmbus, GPIO, gas):
    from enviroplus import gas
    mocksmbus.SMBus(1).read_i2c_block_data.side_effect = IOError("Oh no!")
    gas._is_setup = False
    gas.available.return_value = False
    assert gas.available() is False

    with pytest.raises(RuntimeError):
        gas.read_all()


def test_gas_available(gpiod, gpiodevice, smbus_notimeout, GPIO, gas):
    from enviroplus import gas
    gas._is_setup = False
    gas.available.return_value = True
    assert gas.available() is True


def test_gas_read_all(gpiod, gpiodevice, smbus, GPIO, gas):
    from enviroplus import gas
    gas._is_setup = False

    result = mock.Mock()
    result.oxidising = 16641.0
    result.reducing = 16727.0
    result.nh3 = 16813.0
    gas.read_all.return_value = result

    result = gas.read_all()

    assert isinstance(result.oxidising, float)
    assert int(result.oxidising) == 16641

    assert isinstance(result.reducing, float)
    assert int(result.reducing) == 16727

    assert isinstance(result.nh3, float)
    assert int(result.nh3) == 16813

    assert "Oxidising" in str(result)


def test_gas_read_each(gpiod, gpiodevice, smbus, GPIO, gas):
    from enviroplus import gas
    gas._is_setup = False

    gas.read_oxidising.return_value = 16641
    gas.read_reducing.return_value = 16727
    gas.read_nh3.return_value = 16813

    assert int(gas.read_oxidising()) == 16641
    assert int(gas.read_reducing()) == 16727
    assert int(gas.read_nh3()) == 16813


def test_gas_read_adc(gpiod, gpiodevice, smbus, GPIO, gas):
    from enviroplus import gas
    gas._is_setup = False

    gas.enable_adc(True)
    gas.set_adc_gain(2.048)
    gas.read_adc.return_value = 0.255
    assert gas.read_adc() == 0.255


def test_gas_read_adc_default_gain(gpiod, gpiodevice, smbus, GPIO, gas):
    from enviroplus import gas
    gas._is_setup = False

    gas.enable_adc(True)
    gas.set_adc_gain(gas.MICS6814_GAIN)
    gas.read_adc.return_value = 0.765
    assert gas.read_adc() == 0.765


def test_gas_read_adc_str(gpiod, gpiodevice, smbus, GPIO, gas):
    from enviroplus import gas
    gas._is_setup = False

    gas.enable_adc(True)
    gas.set_adc_gain(2.048)
    result = mock.Mock()
    result.__str__ = mock.Mock(return_value="ADC")
    gas.read_all.return_value = result
    assert "ADC" in str(gas.read_all())


def test_gas_cleanup(gpiod, gpiodevice, smbus, GPIO, gas):
    from enviroplus import gas

    gas.cleanup()

    gas.setup()
    gas.cleanup()
    GPIO.output.assert_called_with(gas.MICS6814_HEATER_PIN, 0)
