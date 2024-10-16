class Cred():
    """
    A class representing a credential with various attributes.

    Attributes:
        name (str): The name of the credential.
        url (str): The URL associated with the credential.
        email (str): The email address related to the credential.
        login (str): The login username or identifier.
        password (str): The password for the credential.
        note (str): Additional notes about the credential.
        share (str): Information on who the credential is shared with.
    """

    def __init__(
        self,
        # index=None,
        name=None,
        url=None,
        email=None,
        login=None,
        password=None,
        note=None,
        share=None
    ):
        """
        Initializes a new Cred object.

        Args:
            # index: The index of the credential (optional).
            name: The name of the credential.
            url: The URL associated with the credential.
            email: The email address related to the credential.
            login: The login username or identifier.
            password: The password for the credential.
            note: Additional notes about the credential.
            share: Information on who the credential is shared with.

        Returns:
            A new Cred object.
        """
        # self.index = index
        self.name = name
        self.url = url
        self.email = email
        self.login = login
        self.password = password
        self.note = note
        self.share = share

    def to_dict(self):
        """
        Converts the Cred object to a dictionary.

        Returns:
            A dictionary representation of the Cred object.
        """
        return {
            # 'index': self.index,
            'name': self.name,
            'url': self.url,
            'email': self.email,
            'login': self.login,
            'password': self.password,
            'note': self.note,
            'share': self.share,
        }

    def isempty(self):
        """
        Checks if the Cred object has all attributes empty.

        Returns:
            True if all attributes are empty, False otherwise.
        """
        isempty = (len(self.name) == 0)
        isempty &= (len(self.url) == 0)
        isempty &= (len(self.email) == 0)
        isempty &= (len(self.login) == 0)
        isempty &= (len(self.password) == 0)
        isempty &= (len(self.note) == 0)
        isempty &= (len(self.share) == 0)
        return isempty

    @staticmethod
    def from_dict(dict_in):
        """
        Creates a Cred object from a dictionary.

        Args:
            dict_in: The input dictionary containing the attributes of the credential.

        Returns:
            A new Cred object initialized with the values from the dictionary.
        """
        return Cred(
            # index=dict_in["index"],
            name=dict_in["name"],
            url=dict_in["url"],
            email=dict_in["email"],
            login=dict_in["login"],
            password=dict_in["password"],
            note=dict_in["note"],
            share=dict_in["share"]
        )

    @staticmethod
    def mock():
        """
        Creates a mock Cred object with example values.

        Returns:
            A new Cred object with pre-filled attributes for testing purposes.
        """
        return Cred(
            # index=1,
            name="example_name",
            url="example_url",
            email="example_email",
            login="example_login",
            password="example_password",
            note="example_note",
            share="example_share"
        )
