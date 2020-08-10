from django.shortcuts import render, redirect
from django.views import generic
from .models import Object, Contract, Material, RequestForMaterial
from transliterate import slugify


class HomeView(generic.ListView):
    template_name = 'index.html'
    queryset = Object.objects.all()


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


class ContractDetailView(generic.ListView):
    template_name = 'appbase/contract/detail.html'
    # model = Material
    queryset = Material.objects.all()

    def get(self, request, *args, **kwargs):
        contract_slug = self.kwargs['contract_slug']
        object_slug = self.kwargs['slug']
        contract = Contract.objects.get(slug=contract_slug)

        materials = Material.objects.filter(contract=contract)
        self.extra_context = {
            'materials': materials,
            'contract': contract,
            'requests': RequestForMaterial.objects.filter(contract=contract)

        }
        return super().get(request, *args, **kwargs)


class ContractAddView(generic.TemplateView):
    template_name = 'appbase/contract/add.html'

    def get(self, request, *args, **kwargs):
        object_slug = self.kwargs['slug']
        object = Object.objects.get(slug=object_slug)
        self.extra_context = {
            'object': object,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        object_id = request.POST['object']
        name = request.POST['name']
        contractor = request.POST['contractor']
        contract = request.FILES['contract']
        number_contract = request.POST['number_contract']
        status = request.POST['status']
        slug = slugify(name)

        Contract.objects.create(contstruct_object_id=object_id, name=name, slug=slug, contract=contract, contractor=contractor, number_contract=number_contract, status=status)

        return redirect('/objects/'+self.kwargs['slug'])


class ContractEditView(generic.TemplateView):
    template_name = 'appbase/contract/edit.html'

    def get(self, request, *args, **kwargs):
        object_slug = self.kwargs['slug']
        contract_slug = self.kwargs['contract_slug']
        object = Object.objects.get(slug=object_slug)
        contract = Contract.objects.get(slug=contract_slug)
        self.extra_context = {
            'object': object,
            'contract': contract
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        contract_slug = self.kwargs['contract_slug']
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

        return redirect('/objects/'+self.kwargs['slug'])

def contract_delete(request, slug):
    contract_id = request.POST['contract']
    Contract.objects.get(id=contract_id).delete()
    return redirect('/objects/' + slug)


class RequestAddView(generic.TemplateView):
    template_name = 'appbase/contract/request/add.html'

    def get(self, request, *args, **kwargs):
        object_slug = self.kwargs['slug']
        contract_slug = self.kwargs['contract_slug']
        contract = Contract.objects.get(slug=contract_slug)
        self.extra_context = {
            # 'object': object,
            'contract': contract
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        contract = Contract.objects.get(id=request.POST['contract'])
        name = request.POST['name']
        file = request.FILES['request']
        RequestForMaterial.objects.create(contract=contract, name=name, file=file)
        return redirect('/objects/'+self.kwargs['slug']+ '/' + contract.slug)