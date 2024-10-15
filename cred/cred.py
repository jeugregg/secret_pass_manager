class Cred():
    '''
        'name': name,
        'url': url,
        'username': username,
        'password': password,
        'shared_to': shared_to,
        'note': note,

            name: "example_name".to_string(),
            url: "example_url".to_string(),
            email: "example_email".to_string(),
            login: "example_login".to_string(),
            password: "example_password".to_string(),
            note: "example_note".to_string(),
            share: "example_share".to_string(),
        '''

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
        # self.index = index
        self.name = name
        self.url = url
        self.email = email
        self.login = login
        self.password = password
        self.note = note
        self.share = share

    def to_dict(self):
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

    @staticmethod
    def from_dict(dict_in):
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
