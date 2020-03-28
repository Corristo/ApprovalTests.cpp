import unittest

from scripts.prepare_release import PrepareRelease


class TestPrepareRelease(unittest.TestCase):
    def test_update_features_with_new_features(self):
        content = f'''
toc

## v.x.y.z

{self.new_feature_text()}

{self.old_feature_text()}

'''
        expected_new_content = '''
toc

## v.x.y.z

## v.1.2.4

### New Feature

New feature details.

## v.1.2.3

### Old Feature

Old feature details.

'''
        old_version = "v.1.2.3"
        new_version = "v.1.2.4"
        action = PrepareRelease.prepare_update_features_page(old_version, new_version, content)
        new_content = action("", lambda _, old, new: content.replace(old, new))
        self.assertEqual(expected_new_content, new_content)

    def test_update_features_with_no_new_features(self):
        content = '''
toc

## v.x.y.z

## v.1.2.3

### Old Feature

Old feature details.

'''
        old_version = "v.1.2.3"
        new_version = "v.1.2.4"
        action = PrepareRelease.prepare_update_features_page(old_version, new_version, content)
        new_content = action("", lambda text: f'CHECK: {text}')
        self.assertEqual(new_content, 'CHECK: the Features page is empty: are you sure you want this?')

    def new_feature_text(self):
        return '''### New Feature

New feature details.'''

    def old_feature_text(self):
        return '''## v.1.2.3

### Old Feature

Old feature details.'''


if __name__ == '__main__':
    unittest.main()
