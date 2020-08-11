from django.shortcuts import render, redirect
from django.views import generic
from .models import Object, Contract, Material, RequestForMaterial, InvoiceForPayment
from transliterate import slugify
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class HomeView(generic.ListView):
    template_name = 'index.html'
    queryset = Object.objects.all()


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ObjectDetailView(generic.DetailView):
    template_name = 'appbase/object_detail.html'
    model = Object

    def get(self, request, *args, **kwargs):
        object_slug = self.kwargs.get(self.slug_url_kwarg, None)

        contracts = Contract.objects.filter(contstruct_object__slug=object_slug)

        self.extra_context = {
            'contracts': contracts,
        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ContractDetailView(generic.TemplateView):
    template_name = 'appbase/contract/detail.html'

    # model = Material
    # queryset = Material.objects.all()

    def get(self, request, *args, **kwargs):
        contract_slug = self.kwargs['slug']
        contract = Contract.objects.get(slug=contract_slug)
        materials = Material.objects.filter(contract=contract)
        self.extra_context = {
            'materials': materials,
            'contract': contract,
            'requests': RequestForMaterial.objects.filter(contract=contract),
            'object': Object.objects.get(slug=contract.contstruct_object.slug),

        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ContractAddView(generic.TemplateView):
    template_name = 'appbase/contract/add.html'

    def get(self, request, *args, **kwargs):
        print('asd')
        self.extra_context = {
            'object': Object.objects.get(slug=self.kwargs['slug']),
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        object_id = request.POST['object']
        name = request.POST['name']
        contractor = request.POST['contractor']
        contract = request.FILES['contract']
        number_contract = request.POST['number_contract']
        status = request.POST['status']
        if slugify(name) == None:
            slug = name
        else:
            slug = slugify(name)

        Contract.objects.create(contstruct_object_id=object_id, name=name, slug=slug, contract=contract,
                                contractor=contractor, number_contract=number_contract, status=status)

        return redirect('/objects/' + Object.objects.get(id=object_id).slug)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ContractEditView(generic.TemplateView):
    template_name = 'appbase/contract/edit.html'

    def get(self, request, *args, **kwargs):

        contract_slug = self.kwargs['slug']

        contract = Contract.objects.get(slug=contract_slug)
        self.extra_context = {
            'object': Object.objects.get(slug=contract.contstruct_object.slug),
            'contract': contract
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        contract_slug = self.kwargs['slug']
        contract = Contract.objects.get(slug=contract_slug)
        object_id = request.POST['object']
        name = request.POST['name']
        if request.FILES:
            contract_file = request.FILES['contract']
        else:
            contract_file = contract.contract
        contractor = request.POST['contractor']

        number_contract = request.POST['number_contract']
        status = request.POST['status']
        slug = slugify(name)

        contract.name = name
        contract.contract = contractor
        contract.contract = contract_file
        contract.number_contract = number_contract
        contract.status = status
        contract.save()

        return redirect('/objects/' + contract.contstruct_object.slug)


@login_required(login_url='/accounts/login/')
def contract_delete(request):
    contract = Contract.objects.get(id=int(request.POST['contract']))
    red = contract.contstruct_object.slug
    contract.delete()

    return redirect('/objects/' + red)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class RequestAddView(generic.TemplateView):
    template_name = 'appbase/contract/request/add.html'

    def get(self, request, *args, **kwargs):
        contract = Contract.objects.get(slug=self.kwargs['slug'])
        self.extra_context = {
            'contract': contract,
            'object': Object.objects.get(contract=contract)
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        contract = Contract.objects.get(id=request.POST['contract'])
        name = request.POST['name']
        file = request.FILES['request']
        RequestForMaterial.objects.create(contract=contract, name=name, file=file)
        return redirect('/contract/detail/' + contract.slug)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class RequestEditView(generic.TemplateView):
    template_name = 'appbase/contract/request/edit.html'

    def get(self, request, *args, **kwargs):
        request_mat = RequestForMaterial.objects.get(id=self.kwargs['id'])
        self.extra_context = {
            'request_mat': request_mat,
            'object': Object.objects.get(contract__request=request_mat)
        }

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request_mat = RequestForMaterial.objects.get(id=request.POST['id'])

        # contract_slug = self.kwargs['contract_slug']
        # contract = Contract.objects.get(slug=contract_slug)
        # object_id = request.POST['object']
        name = request.POST['name']
        if request.FILES:
            request_mat_file = request.FILES['request']
        else:
            request_mat_file = request_mat.file

        request_mat.name = name
        request_mat.file = request_mat_file
        request_mat.save()

        return redirect('/contract/detail/' + request_mat.contract.slug)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class RequestDetailView(generic.TemplateView):
    template_name = 'appbase/contract/request/detail.html'

    def get(self, request, *args, **kwargs):
        request_mat = RequestForMaterial.objects.get(id=self.kwargs['id'])

        self.extra_context = {
            'request_mat': request_mat,
            'object': Object.objects.get(slug=request_mat.contract.contstruct_object.slug),
        }
        return super().get(request, *args, **kwargs)


@login_required(login_url='/accounts/login/')
def request_delete(request):
    request_mat = RequestForMaterial.objects.get(id=request.POST['id'])
    red = '/contract/detail/' + request_mat.contract.slug
    request_mat.delete()

    return redirect(red)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InvoiceAddView(generic.TemplateView):
    template_name = 'appbase/contract/request/invoice/add.html'

    def get(self, request, *args, **kwargs):
        request_mat = RequestForMaterial.objects.get(id=self.kwargs['id'])
        self.extra_context = {
            'request_mat': request_mat,
            'object': Object.objects.get(contract__request=request_mat)
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request_mat = RequestForMaterial.objects.get(id=int(request.POST['id']))
        file = request.FILES['invoice']
        InvoiceForPayment.objects.create(request_mat=request_mat, file=file)
        return redirect('/request/detail/' + str(request_mat.id))


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InvoiceEditView(generic.TemplateView):
    template_name = 'appbase/contract/request/invoice/edit.html'

    def get(self, request, *args, **kwargs):
        invoice = InvoiceForPayment.objects.get(id=int(self.kwargs['id']))

        self.extra_context = {
            'invoice': invoice,
            'object': Object.objects.get(contract__request__invoice=invoice)
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        invoice = InvoiceForPayment.objects.get(id=int(request.POST['id']))
        file = request.FILES['invoice']
        invoice.file = file
        invoice.save()
        return redirect('/request/detail/' + str(invoice.request_mat.id))


@login_required(login_url='/accounts/login/')
def invoice_delete(request):
    invoice = InvoiceForPayment.objects.get(id=request.POST['id'])
    red = '/request/detail/' + str(invoice.request_mat.id)
    invoice.delete()

    return redirect(red)
