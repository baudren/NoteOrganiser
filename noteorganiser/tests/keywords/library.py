from robot.api.deco import keyword


class LibraryKeywords(object):

    def library_tab_should_be_opened(self):
        raise NotImplementedError

    @keyword('create a notebook named ${name}')
    def create_a_notebook_named(self, name):
        raise NotImplementedError

    @keyword('the notebook ${name} should be present')
    def the_notebook_should_be_present(self, name):
        raise NotImplementedError

    @keyword('the notebook ${name} should be absent')
    def the_notebook_should_be_absent(self, name):
        return not the_notebook_should_be_present()

    @keyword('remove notebook ${name}')
    def remove_notebook(self, name):
        raise NotImplementedError

    @keyword('create a folder named ${name}')
    def create_a_folder_named(self, name):
        raise NotImplementedError

    @keyword('the folder ${name} should be present')
    def the_folder_should_be_present(self, name):
        raise NotImplementedError

    @keyword('the folder ${name} should be absent')
    def the_folder_should_be_absent(self, name):
        return not the_folder_should_be_present()

    @keyword('remove folder ${name}')
    def remove_folder(self, name):
        raise NotImplementedError
