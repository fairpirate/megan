import unittest
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.modules_engine import (
    generate_file, execute_code, build_module, 
    delete_file, write_file, list_modules, list_outputs,
    run_shell
)
from core.orchestrator import detect_intent, execute_actions

class TestMeganTools(unittest.TestCase):

    def setUp(self):
        self.test_file = "test_artifact.txt"
        self.test_content = "Hello MEGAN"
        self.test_module = "test_mod_xyz"

    def tearDown(self):
        # Cleanup
        delete_file(f"outputs/{self.test_file}")
        delete_file(f"modules/{self.test_module}.py")
        delete_file("test_direct_write.txt")

    def test_generate_file(self):
        res = generate_file(self.test_file, self.test_content, "txt")
        self.assertEqual(res["status"], "ok")
        self.assertTrue(Path(res["path"]).exists())
        self.assertIn(self.test_file.split('.')[0], res["filename"])

    def test_execute_code(self):
        code = "print('success')"
        res = execute_code(code)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["stdout"].strip(), "success")

    def test_build_module(self):
        code = "def hello(): return 'hi'"
        res = build_module(self.test_module, "Test description", code)
        self.assertEqual(res["status"], "ok")
        self.assertTrue(Path(res["path"]).exists())
        self.assertIn(self.test_module, list_modules())

    def test_write_and_delete_file(self):
        path = "test_direct_write.txt"
        content = "Direct write content"
        
        # Test Write
        res_w = write_file(path, content)
        self.assertEqual(res_w["status"], "ok")
        self.assertTrue(Path(res_w["path"]).exists())
        self.assertEqual(Path(res_w["path"]).read_text(), content)
        
        # Test Delete
        res_d = delete_file(path)
        self.assertEqual(res_d["status"], "ok")
        self.assertFalse(Path(res_d["path"]).exists())

    def test_orchestrator_detection(self):
        response = "I will do this: [SAVE_FILE: hello.txt]world"
        actions = detect_intent(response)
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["type"], "save_file")
        self.assertEqual(actions[0]["filename"], "hello.txt")
        self.assertEqual(actions[0]["content"], "world")

    def test_orchestrator_delete_detection(self):
        response = "Removing it: [DELETE_FILE: temp.txt]"
        actions = detect_intent(response)
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["type"], "delete_file")
        self.assertEqual(actions[0]["path"], "temp.txt")

    def test_shell_command(self):
        res = run_shell("echo 'hello shell'")
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["stdout"].strip(), "hello shell")

if __name__ == "__main__":
    unittest.main()
