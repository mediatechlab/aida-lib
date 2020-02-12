def create_forecast(weather_label, condition, temp, time_of_day):
    node = create_match(weather_label, now=Choices(
        'right now', 'now'), default=time_of_day + ',')
    verb = Branch(~condition.in_ctx(), create_match(
        weather_label, now='is', default='will be'), 'will')

    return (node | 'the weather' | verb | create_alt(condition, 'remain the same') | 'with a temperature of' | (temp | 'degrees')).sentence()


if __name__ == "__main__":
    import sys
    sys.path.append('.')
    from aida import render, Choices, create_match, Var, Ctx, Repeat, Injector, create_alt, Branch

    ctx = Ctx()

    # define overall structure
    weather_label = Var('time')
    condition = Var('cond')
    temp = Var('temp')
    tod = Var('tod')
    forecast = create_forecast(weather_label, condition, temp, tod)
    inj = Injector([weather_label, condition, temp, tod], forecast)
    repeat = Repeat(inj)

    # assign data
    data = [{'time': 'now', 'cond': 'rainy', 'temp': 20, 'tod': None},
            {'time': 'afternoon', 'cond': 'clear',
                'temp': 15, 'tod': 'in the afternoon'},
            {'time': 'evening', 'cond': 'clear', 'temp': 12, 'tod': 'in the night'}]
    inj.assign(data)
    repeat.assign(len(data))

    # print result
    print(render(repeat))
