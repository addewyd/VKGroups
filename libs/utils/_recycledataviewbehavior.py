# Write by Tito.

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior


class _RecycleDataViewBehavior(RecycleDataViewBehavior, BoxLayout):
    _latest_data = None
    _rv = None
    
    def refresh_view_attrs(self, rv, index, data):
        self._rv = rv
        
        if self._latest_data is not None:
            self._latest_data['height'] = self.height
        self._latest_data = data
        super(_RecycleDataViewBehavior, self).refresh_view_attrs(rv, index, data)
        
    def on_height(self, instance, value):
        data = self._latest_data

        if data is not None and data['height'] != value:
            data['height'] = value
            self._rv.refresh_from_data()
