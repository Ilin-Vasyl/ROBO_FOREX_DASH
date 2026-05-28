def create_options(values, first_label):

    return (
        [{'label': first_label, 'value': 'ALL'}] +
        [{'label': x, 'value': x} for x in sorted(values)]
    )


def get_filter_options(df):

    pairs = sorted(
        df['Item']
        .dropna()
        .unique()
    )

    pair_options = create_options(
        pairs,
        'All pairs'
    )

    robo_type_options = create_options(
        df['Robo_Type']
        .dropna()
        .unique(),
        'All types'
    )

    robo_name_options = create_options(
        df['Robo_Name']
        .dropna()
        .unique(),
        'All robots'
    )

    return (
        pair_options,
        robo_type_options,
        robo_name_options
    )


def get_dependent_filter_options(df,
                                 selected_pair,
                                 selected_robo_type,
                                 selected_robo_name):

    pair_df = df.copy()

    if selected_robo_type != 'ALL':
        pair_df = pair_df[
            pair_df['Robo_Type'] == selected_robo_type
        ]

    if selected_robo_name != 'ALL':
        pair_df = pair_df[
            pair_df['Robo_Name'] == selected_robo_name
        ]

    robo_type_df = df.copy()

    if selected_pair != 'ALL':
        robo_type_df = robo_type_df[
            robo_type_df['Item'] == selected_pair
        ]

    if selected_robo_name != 'ALL':
        robo_type_df = robo_type_df[
            robo_type_df['Robo_Name'] == selected_robo_name
        ]

    robo_name_df = df.copy()

    if selected_pair != 'ALL':
        robo_name_df = robo_name_df[
            robo_name_df['Item'] == selected_pair
        ]

    if selected_robo_type != 'ALL':
        robo_name_df = robo_name_df[
            robo_name_df['Robo_Type'] == selected_robo_type
        ]

    pair_options = create_options(
        pair_df['Item']
        .dropna()
        .unique(),
        'All pairs'
    )

    robo_type_options = create_options(
        robo_type_df['Robo_Type']
        .dropna()
        .unique(),
        'All types'
    )

    robo_name_options = create_options(
        robo_name_df['Robo_Name']
        .dropna()
        .unique(),
        'All robots'
    )

    return (
        pair_options,
        robo_type_options,
        robo_name_options
    )