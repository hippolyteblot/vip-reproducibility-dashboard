import pytest

from girder.plugin import loadedPlugins


# fixture db
@pytest.fixture
def db():
    
    from girder.utility import config

    # connect to the database

    # end of fixture
    yield

# fixture fsAssetstore
@pytest.fixture
def fsAssetstore(db):
    assetstore = {
        'type': 'filesystem',
        'name': 'Test',
        'root': '/tmp/girder_test_assetstore'
    }

    yield assetstore
    
# fixture admin
@pytest.fixture
def admin(db):
    from girder.models.user import User

    admin = User().createUser(
        login='admin',
        password='password',
        firstName='Admin',
        lastName='Admin',

        admin=True
    )

    yield admin


# fixture server
@pytest.fixture
def server(db, fsAssetstore, admin):
    from girder.models.folder import Folder
    from girder.models.item import Item
    from girder.models.upload import Upload
    from girder.models.user import User
    from girder.utility.server import setup as setupServer

    server = setupServer()
    server.request = server.getRequestThread(userId=admin['_id'])
    server.model('user').setUserAdmin(admin, True)
    server.model('user').createUser(
        login='test',
        password='password',
        firstName='Test',
        lastName='User',

        admin=True
    )
    server.model('user').createUser(
        login='test2',
        password='password',
        firstName='Test',
        lastName='User',

        admin=True
    )

    # create a folder
    folder = Folder().createFolder(
        parent=admin,
        name='test',
        parentType='user',
        public=True,
        creator=admin
    )

    # create an item
    item = Item().createItem(
        name='test',
        creator=admin,
        folder=folder
    )

    # create an upload
    upload = Upload().createUploadToFile(
        obj=item,
        user=admin,
        size=0,
        name='test.csv',
        mimeType='text/csv'
    )

    # create a file
    file = server.model('file').load(upload['fileId'], force=True)
    
    # end of fixture
    yield server



#@pytest.mark.plugin('auto_feather')
def test_import(server):
    assert 'auto_feather' in loadedPlugins()

    def upload_file():
        # upload a file
        server.request(
            path='/file',
            method='POST',
            user=server.model('user').findOne({'login': 'admin'}),
            params={
                'parentType': 'folder',
                'parentId': '5e8f1b7a8d777f0001f2b0a1',
                'name': 'test.csv',
                'size': 0,
                'mimeType': 'text/csv'
            }
        )
    
    upload_file()
