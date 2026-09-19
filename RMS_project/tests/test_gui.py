import unittest
from unittest.mock import MagicMock, patch

from gui import RecordTab, TravelAgentApp
from validation import ValidationError


class TestGUIBehaviour(unittest.TestCase):

    def make_record_tab(self):
        """
        Create a lightweight RecordTab instance without starting Tkinter.
        Only the attributes needed by the event methods are supplied.
        """
        tab = object.__new__(RecordTab)
        tab.controller = MagicMock()
        tab.record_type = "CLIENT"
        tab.selected_id = None
        tab.search_var = MagicMock()
        tab.get_form_values = MagicMock(
            return_value={
                "clientName": "Alice Smith",
                "email": "alice@example.com",
                "addressLineOne": "1 Test Street",
                "addressLineTwo": "",
                "addressLineThree": "",
                "city": "Manchester",
                "state": "Greater Manchester",
                "zipCode": "M1 1AE",
                "country": "United Kingdom",
                "phoneNumber": "07123456789",
            }
        )
        tab.populate_tree = MagicMock()
        tab.refresh_tree = MagicMock()
        tab.clear_form = MagicMock()
        return tab

    def test_search_delegates_to_controller_and_displays_results(self):
        tab = self.make_record_tab()
        expected = [{"id": 1, "clientName": "Alice Smith"}]

        tab.search_var.get.return_value = "Alice"
        tab.controller.search.return_value = expected

        RecordTab.on_search(tab)

        tab.controller.search.assert_called_once_with(
            "CLIENT",
            "Alice"
        )
        tab.populate_tree.assert_called_once_with(expected)

    def test_update_without_selection_shows_warning_and_does_not_update(self):
        tab = self.make_record_tab()

        with patch("gui.messagebox.showwarning") as warning:
            RecordTab.on_update(tab)

        warning.assert_called_once_with(
            "Warning",
            "Select a record first."
        )
        tab.controller.update_record.assert_not_called()

    def test_delete_requires_confirmation_before_controller_call(self):
        tab = self.make_record_tab()
        tab.selected_id = 7

        with patch(
            "gui.messagebox.askyesno",
            return_value=False
        ) as confirm:
            RecordTab.on_delete(tab)

        confirm.assert_called_once_with(
            "Confirm Delete",
            "Delete selected record?"
        )
        tab.controller.delete_record.assert_not_called()
        tab.refresh_tree.assert_not_called()
        tab.clear_form.assert_not_called()

    def test_delete_after_confirmation_calls_controller(self):
        tab = self.make_record_tab()
        tab.selected_id = 7

        with patch(
            "gui.messagebox.askyesno",
            return_value=True
        ):
            RecordTab.on_delete(tab)

        tab.controller.delete_record.assert_called_once_with(
            "CLIENT",
            7
        )
        tab.refresh_tree.assert_called_once()
        tab.clear_form.assert_called_once()

    def test_close_saves_before_destroying_application(self):
        app = object.__new__(TravelAgentApp)
        app.controller = MagicMock()
        app.destroy = MagicMock()

        TravelAgentApp.on_close(app)

        app.controller.save.assert_called_once()
        app.destroy.assert_called_once()

    def test_controller_validation_error_is_shown_to_user(self):
        """
        The GUI documentation states that controller validation failures
        should be displayed as error dialogs.
        """
        tab = self.make_record_tab()
        tab.controller.create_record.side_effect = ValidationError(
            "Invalid client data"
        )

        with patch("gui.messagebox.showerror") as show_error:
            RecordTab.on_create(tab)

        show_error.assert_called_once_with(
            "Error",
            "Invalid client data"
        )


if __name__ == "__main__":
    unittest.main()
