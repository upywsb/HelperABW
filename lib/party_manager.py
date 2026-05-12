import time

class PartySlot:
    def __init__(self, slot_id):
        self.slot_id = slot_id
        self.is_active = False
        self.hp_min = 0
        self.hp_max = 40
        self.key_bind = ""
        self.cooldown = 1.0
        self.last_used = 0
        # Współrzędne relatywne (0.0 - 1.0)
        self.anchor_x = 0.0
        self.anchor_y = 0.0

    def can_trigger(self, current_hp):
        """Sprawdza czy HP mieści się w zakresie i czy cooldown minął."""
        now = time.time()
        if self.is_active and (self.hp_min <= current_hp <= self.hp_max):
            if now - self.last_used >= self.cooldown:
                return True
        return False

    def mark_used(self):
        self.last_used = time.time()

class PartyManager:
    def __init__(self):
        # Inicjalizacja 8 slotów party
        self.slots = [PartySlot(i) for i in range(1, 9)]
        self.offset_y_ratio = 0.05  # Przykładowy dystans między paskami

    def update_slot_config(self, slot_id, **kwargs):
        slot = self.slots[slot_id - 1]
        for key, value in kwargs.items():
            if hasattr(slot, key):
                setattr(slot, key, value)