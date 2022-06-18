def foo(val: int) -> str:
    if val in [1, 3, 5]:
        raise ValueError()
    else:
        return f'{val}'


gen = map(foo, [1, 2, 3, 4, 5])
cnt = 0

while True:
    try:
        s = gen.__next__()
    except ValueError:
        # If encounters exceptions
        print(f'Oops! Exception at No. {cnt + 1}.')
        continue
    except StopIteration:
        # If iteration reaches the end:
        break
    finally:
        # Count in the 'finally' block:
        cnt += 1

    # Do something with s
    print('Got: ', s)

print(f'Processed {cnt - 1} objects.')
