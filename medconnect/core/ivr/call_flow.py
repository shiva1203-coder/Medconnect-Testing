from utils.logger import get_logger

logger = get_logger(__name__)


class IVRFlow:
    """
    Handles MedConnect IVR call flow logic
    """

    def __init__(self, patient_exists: bool):
        self.patient_exists = patient_exists

    # -----------------------------
    # Language Selection
    # -----------------------------
    def language_menu(self):
        logger.info("IVR: Language selection menu")
        return (
            "Welcome to MedConnect. "
            "For English press 1. "
            "தமிழுக்கு 2 ஐ அழுத்தவும். "
            "हिंदी के लिए 3 दबाएं."
        )

    # -----------------------------
    # Entry Point Menu
    # -----------------------------
    def entry_menu(self):
        if self.patient_exists:
            logger.info("IVR: Returning patient detected")
            return (
                "Welcome back. "
                "Please enter your current area PIN code."
            )

        logger.info("IVR: New patient detected")
        return (
            "You are a new user. "
            "Press 1 to register using Aadhaar. "
            "Press 2 to register manually."
        )

    # -----------------------------
    # Aadhaar Flow
    # -----------------------------
    def aadhaar_menu(self):
        logger.info("IVR: Aadhaar registration selected")
        return (
            "Please enter your 12 digit Aadhaar number "
            "followed by the hash key."
        )

    def otp_menu(self):
        logger.info("IVR: OTP verification step")
        return (
            "An OTP has been sent to your registered mobile number. "
            "Please enter the OTP."
        )

    # -----------------------------
    # Manual Registration Flow
    # -----------------------------
    def manual_name_menu(self):
        return "Please enter your name using the keypad."

    def manual_age_menu(self):
        return "Please enter your age."

    def manual_gender_menu(self):
        return (
            "Press 1 for Male. "
            "Press 2 for Female. "
            "Press 3 for Other."
        )

    # -----------------------------
    # Location & Hospital Selection
    # -----------------------------
    def pincode_menu(self):
        return "Please enter your 6 digit area PIN code."

    def hospital_menu(self, hospitals):
        """
        hospitals: list of hospital names
        """
        message = "Hospitals available in your area. "
        for index, hospital in enumerate(hospitals, start=1):
            message += f"For {hospital}, press {index}. "
        return message

    # -----------------------------
    # Doctor & Slot Selection
    # -----------------------------
    def doctor_menu(self, doctors):
        """
        doctors: list of doctor names
        """
        message = "Available doctors. "
        for index, doctor in enumerate(doctors, start=1):
            message += f"For Doctor {doctor}, press {index}. "
        return message

    def confirmation_menu(self):
        return (
            "Your appointment has been booked successfully. "
            "You will receive the details via SMS. "
            "Thank you for using MedConnect."
        )
    