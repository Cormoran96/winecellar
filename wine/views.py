from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.views import generic
from django.db.models import Sum
from wine.models import Wine
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from wine.models import WineForm
from django.db.models import Q # new
#todo: remove Q
import csv
import io
import xlsxwriter
from xlsxwriter.workbook import Workbook

class WinesView(LoginRequiredMixin, generic.ListView):
    model = Wine
    template_name = 'wine/wine_list.html'

    # Filter user data only
    def get_queryset(self):
        query_set = super().get_queryset()
        return query_set.filter(owner=self.request.user)

# Wine Delete View
class DeleteView(LoginRequiredMixin, DeleteView):
    model = Wine
    success_url = reverse_lazy('wine:wine_list')

# Homepage
def index(request):
    return render(request, 'wine/home.html')

# 'About' page
def about(request):
    return render(request, 'wine/about.html')

# 'Info' page
@login_required
def info(request):
    return render(request, 'wine/info.html')

@login_required
def home(request):
    return render(request, 'wine/index.html')

@login_required
def createWine(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = WineForm(request.POST)
        # Create instance for user data entry
        if form.is_valid():
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.save()
            return HttpResponseRedirect('/wine')
    else:
        form = WineForm()
    return render(request, 'wine/create_form.html', {'form': form})

@login_required
def updateWine(request, pk):
    update = Wine.objects.get(id=pk)
    form = WineForm(instance=update)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = WineForm(request.POST, instance=update)
        # Create instance for user data entry
        if form.is_valid():
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.save()
            return HttpResponseRedirect('/wine')

    return render(request, 'wine/create_form.html', {'form': form})

@login_required
def copyWine(request, pk):
    update = Wine.objects.get(id=pk)
    form = WineForm(instance=update)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = WineForm(request.POST)
        # Create instance for user data entry
        if form.is_valid():
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.save()
            return HttpResponseRedirect('/wine')

    return render(request, 'wine/create_form.html', {'form': form})

class FullView(LoginRequiredMixin, generic.ListView):
    model = Wine
    template_name = 'wine/wine_fullview.html'

    # Filter user data only
    def get_queryset(self):
        query_set = super().get_queryset()
        return query_set.filter(owner=self.request.user)

class WineLog(LoginRequiredMixin, generic.ListView):
    model = Wine
    template_name = 'wine/wine_log.html'

    # Show number of bottles and different wines for each user
    def get_context_data(self, *args, **kwargs):
        context = super(WineLog, self).get_context_data(*args, **kwargs)
        context['bottles_sum'] = Wine.objects.filter(owner=self.request.user).aggregate(Sum('nmbrbottles'))['nmbrbottles__sum']
        context['wines_sum'] = Wine.objects.filter(owner=self.request.user).count()
        return context

    # Filter user data only
    def get_queryset(self):
        query_set = super().get_queryset()
        return query_set.filter(owner=self.request.user).order_by('-editdate')[:30]

# class EditorChartView(generic.ListView):
#     model = Wine
#     template_name = 'wine/charts.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["winedata"] = Wine.objects.all()
#         return context

# Data export
@login_required
def export_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    wines = Wine.objects.filter(owner=request.user)
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="wine_export.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(['Wein', 'Produzent', 'Trauben', 'Jahrgang', 'Land', 'Region', 'Kaufdatum', 'Preis/Fl.', 'Dealer', 'von', 'bis', 'Lagerort', 'Anz.Fl'])
    wines = wines.values_list('winename','producer', 'grapes', 'year', 'country', 'region', 'purchase', 'price', 'dealer', 'drinkfrom', 'drinkto', 'warehouse', 'nmbrbottles')
    for w in wines:
        writer.writerow(w)
    return response

@login_required
    #columns = ['Wein', 'Produzent', 'Trauben', 'Jahrgang', 'Land', 'Region', 'Kaufdatum', 'Preis/Fl.', 'Dealer', 'von', 'bis', 'Lagerort', 'Anz.Fl']
    #rows = Wine.objects.filter(owner=request.user).values_list('winename','producer', 'grapes', 'year', 'country', 'region', 'purchase', 'price', 'dealer', 'drinkfrom', 'drinkto', 'warehouse', 'nmbrbottles')
def export_xls(request):
    data = Wine.objects.filter(owner=request.user)

    output = io.BytesIO()

    workbook = Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    worksheet.write(0, 0, 'Hello, world!')
    workbook.close()

    output.seek(0)

    response = HttpResponse(output.read(),
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=wine_export.xlsx"

    output.close()

    return response

#todo: Check this: https://bravelab.io/blog/how-to-export-orders-in-saleor-io-to-xlsx-file/