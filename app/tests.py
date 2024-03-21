from django.test import TestCase

def search(request):
    # Handle form submission if the request method is POST
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            current_location = form.cleaned_data['current_location']
            destination = form.cleaned_data['destination']
            date = form.cleaned_data['date']
            print('executed 1')
            # Filter search results based on form input
            results = TripSchedule.objects.filter(
                origin__icontains=current_location,
                destination__icontains=destination,
                departure_date=date,
            ).select_related('bus_operator')  # Include bus_operator information
            print('executed 2')
            # Serialize the TripSchedule objects into a JSON-serializable format
            serialized_results = serializers.serialize('json', results)
            print('executed 3')
            # Save serialized search results in session for sorting
            request.session['results'] = serialized_results
            print('executed 4')
    else:
        form = SearchForm()

    # Get sorting preference from query parameters
    sort_by = request.GET.get('sort_by')
    serialized_results = request.session.get('results')
    print('executed 5')
    if serialized_results:
        # Deserialize the serialized search results back into TripSchedule objects
        results = list(serializers.deserialize('json', serialized_results))

        # Extract the TripSchedule objects from the deserialized data
        results = [result.object for result in results]
        print('executed 6')
        # Sort results based on sorting preference
        if sort_by:
            if sort_by == 'price_high_to_low':
                results.sort(key=lambda x: x.price, reverse=True)
            elif sort_by == 'price_low_to_high':
                results.sort(key=lambda x: x.price)
            elif sort_by == 'time_earliest_to_latest':
                results.sort(key=lambda x: x.departure_time)
            elif sort_by == 'time_latest_to_earliest':
                results.sort(key=lambda x: x.departure_time, reverse=True)

    else:
        print('executed 7')
        # Fetch results from the database if not found in the session or if sorting is not requested
        results = None  # Or fetch results from the database

    # Prepare context for rendering template
    context = {'form': form, 'results': results}

    # Return the response
    return render(request, 'search_results.html', context)

