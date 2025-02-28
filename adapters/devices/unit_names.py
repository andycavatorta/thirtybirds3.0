import math

### R O T A R Y   U N I T S ###

PULSES = "PULSES"
DEGREES = "DEGREES"
GRADS = "GRADS"
RADIANS = "RADIANS"
TURNS = "TURNS"


class Rotary_Distance_To_Orientation_Converter:
    PULSES = "PULSES"
    DEGREES = "DEGREES"
    GRADS = "GRADS"
    RADIANS = "RADIANS"
    TURNS = "TURNS"

    def __init__(
        self,
        pulses_per_revolution=1,  # defaut value for cases where pulses are not relevant
    ):
        self.pulses_per_revolution = pulses_per_revolution

    def convert(self, quantity, unit):
        match unit:
            case self.PULSES:
                return quantity % self.pulses_per_revolution
            case self.DEGREES:
                return quantity % 360.0
            case self.GRADS:
                return quantity % 400.0
            case self.RADIANS:
                return quantity % (2 * math.pi)
            case self.TURNS:
                return 0


class Rotary_Unit_Converter:
    PULSES = "PULSES"
    DEGREES = "DEGREES"
    GRADS = "GRADS"
    RADIANS = "RADIANS"
    TURNS = "TURNS"

    def __init__(
        self,
        pulses_per_revolution=1,  # defaut value for cases where pulses are not relevant
    ):
        self.pulses_per_revolution = pulses_per_revolution

    def convert(self, quantity, original_unit, converted_unit):
        match original_unit:
            case self.PULSES:
                match converted_unit:
                    case self.PULSES:
                        return quantity
                    case self.DEGREES:
                        return (quantity / self.pulses_per_revolution) * 360.0
                    case self.GRADS:
                        return (quantity / self.pulses_per_revolution) * 400.0
                    case self.RADIANS:
                        return (quantity / self.pulses_per_revolution) * (2 * math.pi)
                    case self.TURNS:
                        return math.floor(quantity / self.pulses_per_revolution)
            case self.DEGREES:
                match converted_unit:
                    case self.PULSES:
                        return (quantity / 360.0) * self.pulses_per_revolution
                    case self.DEGREES:
                        return quantity
                    case self.GRADS:
                        return (quantity / 360.0) * 400
                    case self.RADIANS:
                        return (quantity / 360.0) * (2 * math.pi)
                    case self.TURNS:
                        return math.floor(quantity / 360.0)
            case self.GRADS:
                match converted_unit:
                    case self.PULSES:
                        return (quantity / 400.0) * self.pulses_per_revolution
                    case self.DEGREES:
                        return (quantity / 400.0) * 360.0
                    case self.GRADS:
                        return quantity
                    case self.RADIANS:
                        return (quantity / 400.0) * (2 * math.pi)
                    case self.TURNS:
                        return math.floor(quantity / 400.0)
            case self.RADIANS:
                match converted_unit:
                    case self.PULSES:
                        return (quantity / (2 * math.pi)) * self.pulses_per_revolution
                    case self.DEGREES:
                        return (quantity / (2 * math.pi)) * 360.0
                    case self.GRADS:
                        return (quantity / (2 * math.pi)) * 400
                    case self.RADIANS:
                        return quantity
                    case self.TURNS:
                        return math.floor(quantity / (2 * math.pi))
            case self.TURNS:
                match converted_unit:
                    case self.PULSES:
                        return quantity * self.pulses_per_revolution
                    case self.DEGREES:
                        return quantity * 360.0
                    case self.GRADS:
                        return quantity * 400
                    case self.RADIANS:
                        return quantity * 2 * math.pi
                    case self.TURNS:
                        return quantity
